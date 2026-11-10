import csv
import os
from datetime import date
from neo4j import GraphDatabase

# the CSVs and config.txt sit next to this script
HERE = os.path.dirname(os.path.abspath(__file__))

# read config.txt by key (URI, USERNAME, PASSWORD), other lines like DATABASE are fine
config = {}
for line in open(os.path.join(HERE, 'config.txt'), encoding='utf-8'):
    if '=' in line:
        key, value = line.strip().split('=', 1)
        config[key.strip()] = value.strip()

driver = GraphDatabase.driver(config['URI'], auth=(config['USERNAME'], config['PASSWORD']))
database = config.get('DATABASE')   # None means the server's default database


def load(name, ints=[], floats=[], dates=[]):
    # read one CSV into a list of dicts, with the right type for every column
    rows = []
    for record in csv.DictReader(open(os.path.join(HERE, name), encoding='utf-8')):
        row = {}
        for col, value in record.items():
            if value == '\\N' or value == '':
                continue   # missing value: leave the property out
            if col in ints:
                value = int(value)
            elif col in floats:
                value = float(value)
            elif col in dates:
                value = date.fromisoformat(value)
            row[col] = value
        rows.append(row)
    return rows


def run(query, rows):
    # send the rows in batches so one transaction does not get too big
    for i in range(0, len(rows), 5000):
        driver.execute_query(query, rows=rows[i:i + 5000], database_=database)


# one uniqueness constraint per label, so MERGE is fast and never duplicates
keys = {'Driver': 'driverId', 'Constructor': 'constructorId', 'Circuit': 'circuitId',
        'Season': 'year', 'Status': 'statusId', 'Race': 'raceId',
        'Result': 'resultId', 'Qualifying': 'qualifyId', 'PitStop': 'eventId'}
for label, key in keys.items():
    driver.execute_query('CREATE CONSTRAINT IF NOT EXISTS FOR (n:' + label + ') REQUIRE n.' + key + ' IS UNIQUE',
                         database_=database)

# ---------- parent nodes first ----------

# a property that is missing from the row is null in Cypher, and SET with null stores nothing

drivers = load('drivers.csv', ints=['driverId', 'number'], dates=['dob'])
run('''
UNWIND $rows AS row
MERGE (d:Driver {driverId: row.driverId})
SET d.driverRef = row.driverRef, d.number = row.number, d.code = row.code,
    d.forename = row.forename, d.surname = row.surname, d.dob = row.dob,
    d.nationality = row.nationality
''', drivers)
print('Driver', len(drivers))

constructors = load('constructors.csv', ints=['constructorId'])
run('''
UNWIND $rows AS row
MERGE (c:Constructor {constructorId: row.constructorId})
SET c.constructorRef = row.constructorRef, c.constructor_name = row.name,
    c.constructor_nationality = row.nationality
''', constructors)
print('Constructor', len(constructors))

circuits = load('circuits.csv', ints=['circuitId', 'alt'], floats=['lat', 'lng'])
run('''
UNWIND $rows AS row
MERGE (c:Circuit {circuitId: row.circuitId})
SET c.circuitRef = row.circuitRef, c.circuit_name = row.name, c.circuit_loc = row.location,
    c.circuit_country = row.country, c.lat = row.lat, c.lng = row.lng, c.alt = row.alt
''', circuits)
print('Circuit', len(circuits))

seasons = load('seasons.csv', ints=['year'])
run('''
UNWIND $rows AS row
MERGE (s:Season {year: row.year})
''', seasons)
print('Season', len(seasons))

status = load('status.csv', ints=['statusId'])
run('''
UNWIND $rows AS row
MERGE (s:Status {statusId: row.statusId})
SET s.status = row.status
''', status)
print('Status', len(status))

races = load('races.csv', ints=['raceId', 'year', 'round', 'circuitId'], dates=['date'])
run('''
UNWIND $rows AS row
MERGE (r:Race {raceId: row.raceId})
SET r.year = row.year, r.round = row.round, r.name = row.name, r.date = row.date, r.time = row.time
WITH r, row
MATCH (c:Circuit {circuitId: row.circuitId})
MATCH (s:Season {year: row.year})
MERGE (r)-[:AT_CIRCUIT]->(c)
MERGE (r)-[:IN_SEASON]->(s)
''', races)
print('Race', len(races))

# ---------- fact nodes ----------

results = load('results.csv',
               ints=['resultId', 'raceId', 'driverId', 'constructorId', 'statusId', 'number', 'grid', 'position',
                     'positionOrder', 'laps', 'milliseconds', 'fastestLap', 'rank'],
               floats=['points', 'fastestLapSpeed'])
run('''
UNWIND $rows AS row
MERGE (r:Result {resultId: row.resultId})
SET r.number = row.number, r.grid = row.grid, r.position = row.position,
    r.positionText = row.positionText, r.positionOrder = row.positionOrder, r.points = row.points,
    r.laps = row.laps, r.time = row.time, r.milliseconds = row.milliseconds,
    r.fastestLap = row.fastestLap, r.rank = row.rank, r.fastestLapTime = row.fastestLapTime,
    r.fastestLapSpeed = row.fastestLapSpeed
WITH r, row
MATCH (ra:Race {raceId: row.raceId})
MATCH (d:Driver {driverId: row.driverId})
MATCH (c:Constructor {constructorId: row.constructorId})
MATCH (s:Status {statusId: row.statusId})
MERGE (r)-[:FOR_RACE]->(ra)
MERGE (r)-[:BY_DRIVER]->(d)
MERGE (r)-[:FOR_CONSTRUCTOR]->(c)
MERGE (r)-[:HAS_STATUS]->(s)
''', results)
print('Result', len(results))

qualifying = load('qualifying.csv',
                  ints=['qualifyId', 'raceId', 'driverId', 'constructorId', 'number', 'position'])
run('''
UNWIND $rows AS row
MERGE (q:Qualifying {qualifyId: row.qualifyId})
SET q.number = row.number, q.position = row.position, q.q1 = row.q1, q.q2 = row.q2, q.q3 = row.q3
WITH q, row
MATCH (ra:Race {raceId: row.raceId})
MATCH (d:Driver {driverId: row.driverId})
MATCH (c:Constructor {constructorId: row.constructorId})
MERGE (q)-[:FOR_RACE]->(ra)
MERGE (q)-[:BY_DRIVER]->(d)
MERGE (q)-[:FOR_CONSTRUCTOR]->(c)
''', qualifying)
print('Qualifying', len(qualifying))

pit_stops = load('pit_stops.csv', ints=['raceId', 'driverId', 'stop', 'lap', 'milliseconds'])
for row in pit_stops:
    # pit_stops has no id column, so we build one: raceId:driverId:stop
    row['eventId'] = str(row['raceId']) + ':' + str(row['driverId']) + ':' + str(row['stop'])
run('''
UNWIND $rows AS row
MERGE (p:PitStop {eventId: row.eventId})
SET p.stop = row.stop, p.lap = row.lap, p.time = row.time, p.duration = row.duration,
    p.milliseconds = row.milliseconds
WITH p, row
MATCH (ra:Race {raceId: row.raceId})
MATCH (d:Driver {driverId: row.driverId})
MERGE (p)-[:FOR_RACE]->(ra)
MERGE (p)-[:BY_DRIVER]->(d)
''', pit_stops)
print('PitStop', len(pit_stops))

# ---------- final check: should print 51113 nodes and 163510 relationships ----------

nodes = driver.execute_query('MATCH (n) RETURN count(n) AS c', database_=database).records[0]['c']
rels = driver.execute_query('MATCH ()-[r]->() RETURN count(r) AS c', database_=database).records[0]['c']
print('nodes', nodes, 'relationships', rels)

driver.close()
