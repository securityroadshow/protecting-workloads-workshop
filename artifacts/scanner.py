# dependencies
import subprocess
import os
import sys

# used to color text
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# validate command line
if len(sys.argv) != 2:
	print('Usage: scanner.py <target DNS or IP>');
	exit(1);

# set target dns
target = sys.argv[1];

# parse HTTP request results
def parse_result(http_result):
	_http_result = ''.join(map(str, http_result))
	if  '403 Forbidden' in _http_result:
		return ('403 Forbidden' , 0)
	elif '200 OK' in _http_result:
		return ('200 OK' , 1)
	elif '404 Not Found' in _http_result:
		return ('404 Not Found' , 2)
	elif '500 Internal Server Error' in _http_result:
		return ('500 Server Error' , 3)
	else:
		return (_http_result , 0);

# tests to execute
tests = [
         {'Name': '--- Canary GET Request' , 'Type': 'Canary' , 'exec_string': "http -v " + target + "/index.php"},
         {'Name': '--- Canary POST Request', 'Type': 'Canary' , 'exec_string': "http -v --form POST " + target + "/index.php"},
         {'Name': '#1 SQLi in Query String' ,  'Type': 'SQLi' , 'exec_string': "http -v '" + target + "/product.php?id=-260479%2F**%2F%2F*!union*%2F%2F**%2F%2F*!select*%2F%2F**%2Fconcat(username%2C0x3a%2Cpassword%2C0x3a%2Cusertype)%2F**%2F%2F*!from*%2F%2F**%2Fjos_users%2F**%2F'"},
		 {'Name': '#1 SQLi in Cookie' , 'Type': 'SQLi' ,  'exec_string': "http -v " + target + "/product.php?id=32574938 'Cookie:PHPSESSID=-260479%2F**%2F%2F*!union*%2F%2F**%2F%2F*!select*%2F%2F**%2Fconcat(username%2C0x3a%2Cpassword%2C0x3a%2Cusertype)%2F**%2F%2F*!from*%2F%2F**%2Fjos_users%2F**%2F'"},

         {'Name': '#1 XSS in Query String' , 'Type': 'XSS' , 'exec_string': "http -v '" + target + "/product.php?id=<script%20src%3D\"http%3A%2F%2F127.0.0.1%2Fxss_malware.js\">'"},
		 {'Name': '#1 XSS in Body' , 'Type': 'XSS' , 'exec_string': "http -v --form POST " + target + " /product.php" + "reviewEmail=Hacker@Hacker.com reviewName=Hacker reviewTitle=Hacked reviewStory='<script>alert(\"Hello World!\")<script/>' reviewSubmit=Submit"},

         {'Name': '#2 Includes Modules' , 'Type': 'Includes' , 'exec_string': "http -v '" + target + "/includes/index.html'"},

		 {'Name': '#3 CSRF Missing' , 'Type': 'CSRF' , 'exec_string': "http -v --form POST " + target + "/form.php" + " orderSubmit=Submit"},
		 {'Name': '#3 CSRF Invalid' , 'Type': 'CSRF' , 'exec_string': "http -v --form POST " + target + "/form.php" + " orderSubmit=Submit  'x-csrf-token:b@d+0k3n198f3c998eb4c24cc168fd6b92b8c95a'"},

         {'Name': '#4 Path Traversal' , 'Type': 'Traversal' , 'exec_string': "http -v '" + target + "/download.php?form=..%2Fmodules%2Freviews.php'"}
        ]

print('##########################################################')
print('# WAF Tests on Target = ' + target)
print('##########################################################')

# list tests
line_width = 25
for single_test in tests:
	print("\nREQUEST: " + single_test['exec_string'])
	results =  subprocess.getstatusoutput(single_test['exec_string'])
	result_string , ret_code = parse_result(results);
	if ret_code == 1 and 'Canary' not in [single_test['Type']]:
		print(bcolors.FAIL  + 'Test Name:' + single_test['Name'].ljust(line_width) + '  Result: ' + result_string + bcolors.ENDC)
	elif ret_code == 0 and "Canary" in single_test['Type']:
		print(bcolors.FAIL  + 'Test Name:' + single_test['Name'].ljust(line_width) + '  Result: ' + result_string + bcolors.ENDC)
	elif ret_code == 2:
		print(bcolors.OKBLUE  + 'Test Name:' + single_test['Name'].ljust(line_width) + '  Result: ' + result_string + bcolors.ENDC)
	elif ret_code == 3:
		print(bcolors.WARNING  + 'Test Name:' + single_test['Name'].ljust(line_width) + '  Result: ' + result_string + bcolors.ENDC)
	else:
		print(bcolors.OKGREEN  + 'Test Name:' + single_test['Name'].ljust(line_width) + '  Result: ' + result_string + bcolors.ENDC)
