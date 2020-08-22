import cs50
import csv

try:
  db = cs50.SQL('sqlite:///../finance.db')
except:
  print('did not find database file')
else:
  with open("companylist.csv", "r", newline="", encoding='utf-8') as csv_file:
      # fieldnames: Name, Code
      csv_reader = csv.DictReader(csv_file)
      # reads all lines in the file and insert into the database
      counter = 0
      for row in csv_reader:
          # print(row['Symbol'], row['Name'], row['Sector'], row['Industry'], row['Summary'])
          counter += 1
          print(counter)
          db.execute("""insert into companies(symbol, name, sector, industry, nasdaq_url)
                        values(?,?,?,?,?)""", 
                        row['Symbol'], row['Name'], row['Sector'], row['Industry'], row['Summary'])