


# set of searches
# run search in prod
# write time results and result set to container
# run search in qa 
# write time results and result set to container
# calculate: time diff, % diff of results, report union/disunion



def runSearch():

	'''
		param: what env? qa, prod [client id???]
		input: a prepared request? a me/product search query
		output: a report object with result set and performance time
	'''

def searchBaseline(env='qa'):

	'''
		input: what env
	'''

	queries = []

	results = []

	for item in queries:
		results.append(runSearch(item))

	with file as f:
		f.write(results)


def test_calculateDifference()

	search1 = input file
	search2 = input file2

	
