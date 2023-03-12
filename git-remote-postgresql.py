#!/usr/bin/python3
import sys
import pexpect
import re
import time
import os
from datetime import datetime

DEBUG = ("1" == os.getenv("GR_PSQL_DEBUG"))

def print_fl(*args,**kwargs):
  print(*args, **kwargs, flush=True)

def dbgw(s):
  global DEBUG
  if DEBUG:
    print_fl(s, file=sys.stderr, end='')

def dbg(s):
  global DEBUG
  if DEBUG:
    print_fl(s, file=sys.stderr)

def cmd_list():
  dbg("in func: cmd_list")
  print_fl(":object-format sha1")
  print_fl("? refs/heads/main")
  print_fl("@refs/heads/main HEAD")
  print_fl("")

def cmd_capabilities():
  dbg("in func: cmd_capabilities")
  print_fl("import")
  print_fl("export")
  print_fl("refspec refs/heads/*:refs/heads/*")
  print_fl("object-format")
  print_fl("")

def commit_block():
  print_fl("commit refs/heads/main")
  obj = time.gmtime(0)
  utcnow = datetime.utcnow()
  curr_time = round(time.time())
  print_fl(f"committer <notexisting@notexisting.com> {curr_time} +0000")
  msg = f"{utcnow}"
  print_fl(f"data {len(msg)}")
  print_fl(msg)
  child = pexpect.spawn("git rev-parse HEAD")
  id = child.readline()
  id = id.decode().strip()
  dbg(f"id: {id}")
  if((not id.startswith("fatal:")) and (len(id)>10) and ("{id}" != "")):
    print_fl(f"from {id}")

def print_file_list(file_list):
  for fl in file_list:
    print(f"M 100644 :{fl['id']} {fl['name']}")
  print_fl("")

def cmd_import_MAIN():
  global db, host, user, password
  dbg("in func: cmd_import")
  l = sys.stdin.readline()
  while l.startswith("import"):
    dbg("  %s" % l)
    l = sys.stdin.readline()
  cmd = " ".join(['pg_dump', '--schema-only', '-d', db, '-U', user , '-W', '-h', host])
  print_fl("reset refs/heads/main")
  dbg(f"cmd: {cmd}")
  child = pexpect.spawn(cmd)
  dbg("get stdout,stderr,stdin")
  child.expect('(?i)password.*')
  dbg("after exp password")
  child.sendline(password)
  child.expect(pexpect.EOF)
  content = child.before.decode()
  line_output = False
  obj_name = None
  obj_type = None
  block = None
  id = 1
  file_list = []
  for line in content.split("\n"):
    if(line.startswith("-- PostgreSQL database dump complete")):
      dbg("dump ended")
      break
    m = re.search('-- Name: ([^;]+); Type: ([^;]+);', line)
    if not m is None:
      if (not block is None):
        if(block.endswith("--\n")):
          block = block[-3:]
        print_fl(f"data {len(block)}")
        print_fl(block)
      block = ""
      line_output = True
      obj_name = "%s.sql" % m.group(1).replace(" ","_")
      obj_type = m.group(2)
      print_fl(f"blob")
      print_fl(f"mark :{id}")
      file_list.append({"id":id, "name":f"{obj_type}/{obj_name}"})
      id += 1
    if line_output:
      block += f"{line}\n"
  if (not block is None):
    print_fl(f"data {len(block)}")
    print_fl(block)
  commit_block()
  print_file_list(file_list)
  print_fl("done")
  print_fl("")
  dbg("end 'get stdout,stderr,stdin'")
  sys.exit(0)

dbg("START")
dbg(sys.argv)
if(sys.argv):
  if(len(sys.argv)==3):
    url = sys.argv[2]
    dbg(url)
    host_and_path = url[url.index('://')+3:]
    dbg(f"host_and_path: {host_and_path}")
    host_and_port = host_and_path[:host_and_path.index('/')]
    dbg(f"host_and_port: {host_and_port}")
    host = host_and_port[:host_and_port.index(":")]
    port = host_and_port[len(host)+1:]
    dbg(f"host: {host}")
    dbg(f"port: {port}")
    db = host_and_path[len(host_and_port)+1:]
    dbg(f"db: {db}")
    user = "itsme"
    password = "itsme"

    while True:
      cmd = sys.stdin.readline()
      cmd = cmd.strip()
      if len(cmd) > 0:
        dbg(f"cmd: {cmd}")
        if(cmd == "capabilities"):
          cmd_capabilities()
        elif(cmd == "list"):
          cmd_list()
        elif(cmd == "import refs/heads/main"):
          cmd_import_MAIN()
