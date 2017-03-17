# use manual setup.py for gmplot: https://github.com/eli-s-goldberg/gmplot
import gmplot
import pandas as pd
import numpy as np


def geocode_address(row):
	"""
	combine multiple rows text data for import into GoogleMapPlotter.geocode(address).
	:param row: dataframe row
	:return: string, concatenated
	"""

	add1 = 'Address Line 1'
	add2 = 'Address Line 2'
	city = 'City'
	state = 'State'

	return '%s %s %s' % (row[add1], row[city], row[state])


def find_facilty_by_characteristic(df, char, char_id):
	"""
	This effectively is an SQL query:
		select * from table where colume_name = some_value.

	:param df: dataframe
	:param char: strin
	g; search term
	:param char_id: string; identifyer term
	:return: df, sliced
	"""
	return df.loc[df[char] == char_id]


def get_lat_longs_from_geocode_addresses(addresses):
	"""

	:param addresses: string
	:return:  arrays; lats and longs of addresses
	"""
	position = []
	for address in addresses:
		while True:
			try:  # a bit of error handling
				position.append(gmplot.GoogleMapPlotter.geocode(address))
				print(address)
				break
			except IndexError:
				print(address, ': location not found')
				break
	lats = [i[0] for i in position]
	longs = [i[1] for i in position]

	return (lats, longs)


# Example:

# 1) import some data. In this case, locations of dialysis facilities
df = pd.read_csv('.data/data.csv')

# 2) find all facilities in TX
df_tx = df.copy(deep=True)
df_tx = find_facilty_by_characteristic(df_tx, 'State', 'TX')
df_tx.to_csv('df_tx.csv')
df_tx[geocode_address] = df_tx.apply(geocode_address, axis=1)

# 3) get texas addresses
TX_addresses = np.array(df_tx[geocode_address].values)
print('how many in TX:', len(TX_addresses))

# 4) get lat longs from geocode addresses
(lats, longs) = get_lat_longs_from_geocode_addresses(TX_addresses)
np.save('lats', lats)
np.save('longs', longs)

# 5) use heavily modified gmplot API to plot scatter
lats = np.load('lats.npy')
longs = np.load('longs.npy')
titles = TX_addresses
gmap = gmplot.GoogleMapPlotter(lats[0], longs[0], 5)
gmap.scatter(lats, longs, s=90, marker=True, alpha=0.1, titles=titles)
gmap.draw("gmaps_scatter.html", api_key='AIzaSyCEI1cq8S32URnYNb-4tcHVjFyNbCkGLu4')

# 5) use heaviily modified gmplot API to plot heatmap
gmap.heatmap(lats, longs, threshold=10, radius=100)
gmap.draw_heatmap_gapi_style("gmaps_heat.html", api_key='AIzaSyCEI1cq8S32URnYNb-4tcHVjFyNbCkGLu4')
