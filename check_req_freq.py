#!/usr/bin/env python

import os, sys, datetime, json, traceback, re, signal, math


summary = { '10':0, '20':0, '30':0, '40':0, '50':0, '60':0, '70':0, '80':0, '90':0, '100':0,
    '110':0, '120':0, '130':0, '140':0, '150':0, '160':0, '170':0, '180':0, '190':0, '200+':0 }
tmp_stats = {}



exiting = False

def signal_handler(signal, frame):
    global exiting, summary
    print json.dumps(summary)
    print 'Ctrl+C'
    exiting = True
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def get_str(d, k):
    v = d.get(k)
    if isinstance(v, basestring):
        v = v.encode('ascii', 'ignore')
    else:
        v = '%s' % (v,)
    return v

def parse_line(line):

    v = line.split(' - ')
    c = ' - '.join(v[3:])
    
    j = None
    try:
        j = json.loads(c)
    except ValueError:
        # skip json decode error
        return

    ts = int(j[0])
    stat = j[2]
    
    if stat[0] != 'execute_batch' :
        return

    req = stat[1]
    
    snsid = req.get('fb_sig_user')
    queue = req.get('queue')
    if not queue or not isinstance(queue, list):
        return
    
    batch_count = len(queue)

    if snsid not in tmp_stats:
        tmp_stats[snsid] = {}
    
    t = tmp_stats[snsid].get('t')
    cnt = tmp_stats[snsid].get('cnt', 0)
    if not t:
        tmp_stats[snsid]['t'] = ts
        tmp_stats[snsid]['cnt'] = batch_count
    elif ts - t < 60 :
        # print '%s, %s' % (snsid, ts - t)
        tmp_stats[snsid]['cnt'] += batch_count
    else :
        tmp_stats.pop(snsid, None);
        qf = float(cnt + batch_count) / ( ts - t ) * 60
        print '%s,%d,%d' % (snsid, qf, (ts - t))

        sk = math.ceil(qf / 10) * 10
        if sk >= 200 :
            sk = '200+'
        else :
            sk = '%d' % (sk,)

        summary[sk] += 1


def parse_file(filename):
    fp = open(filename, 'r')
    if fp:
        for line in fp:

            if exiting:
                break

            line = line.strip()
            try:
                parse_line(line)
            except:
                err_msg = "Unexpected error: %s" % ( traceback.format_exc(), )
                print >> sys.stderr, err_msg

    else:
        print >> sys.stderr, 'open failed'


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print >> sys.stderr, 'invalid arguments'
        sys.exit()

    filename = sys.argv[1]
    
    parse_file(filename)

    print json.dumps(summary)

    print >> sys.stderr, 'end'


