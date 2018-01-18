from manage import get_stats


dv = 0
fin = 0
op = 0

for r in get_stats():
	id, frage, downvotes, answers = r
	if downvotes >= 3:
		dv += 1
		continue
	if answers >= 100:
		fin += 1
	else:
		op += 1
	print(id, answers, downvotes, frage)

print("Downvoted: {}".format(dv))
print("Finished: {}".format(fin))
print("Open: {}".format(op))
