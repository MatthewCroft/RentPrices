import csv

def get_zips():
	m = {}
	with open('zip_code_database.csv') as f:
		f_csv = csv.reader(f)
		headers = next(f_csv)
		for row in f_csv:
			m[row[0]] = row
	return m

if __name__ == '__main__':
	get_zips()