"""Apply date_edits.json to a work tree with a given date (chat-side, for gates before packaging). usage: TREE EDITS_JSON DATE"""
import sys, json, os
tree, edits, day = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3]
for e in edits:
    p = os.path.join(tree, e['file']); s = open(p, encoding='utf-8', newline='').read()
    assert s.count(e['old']) == e['count'], (e['label'], s.count(e['old']))
    open(p, 'w', encoding='utf-8', newline='').write(s.replace(e['old'], e['new'].replace('{TODAY}', day)))
print('applied', len(edits), 'edits with', day)
