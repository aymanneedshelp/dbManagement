import mysql.connector as connector
import getpass
import pickle
import string
import sys, subprocess
try:
	from tabulate import tabulate
except:
	subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate"])
	from tabulate import tabulate

sqlpass=str()

#To check if inputs are empty
def Empty(a):
	if a == "":
		print("You cannot leave this field empty!")
		print()
		return True
	else:
		return False

#To ensure that no inputted field is empty
def userinput(y):
    while True:
        x = input(y)
        if Empty(x):
            print()
        else:
            return x

#To input numbers without exceptions
def intInput(x):
    while True:
        a = userinput(x)
        if a.isdigit():
            b = int(a)
            break
        else:
            print("MUST INPUT A NUMBER!!!")
        print()
    return b

#To check if the inputted value is of the correct format
def isDate(x):
    t=0
    if type(x) == str:
        if len(x) == 10:
            for i in range(10):
                if i == 4 or i == 7:
                    if x[4] == x[7] == '-':
                        pass
                    else:
                        t=1
                else:
                    if x[i] in '0123456789':
                        pass
                    else:
                        t=3
        else:
            t=1
    else:
        t=1
    if t==0:
        return True
    elif t==1:
        print("Date is not of format <YYYY-MM-DD> as a string")
        return False
    elif t==2:
        print("Entered date is invalid")
        return False

#To master login allowing for changes in HR
def masterLogin():
	print("****MASTER LOGIN****")
	try:
		f=open('master.dat','rb')
		l=pickle.load(f)
		check=l[0]
		f.close()
		flag=False
		while flag == False:
			password=getpass.getpass(prompt="Enter Master Password: ")
			if Empty(password):
				flag = False
			else:
				if check==password:
					flag=True
					print("Logged in as master, now you can create a new User")
					print()
					newUser()
				else:
					print("Wrong password entered try again. ")
	except FileNotFoundError:
		flag=False
		print("Create the master password only HR can access ")
		while flag == False:
			password=getpass.getpass(prompt="Enter Password: ")
			if Empty(password):
				flag = False
			else:
				if len(password)>8:
					f=open('master.dat','wb')
					l=[password]
					pickle.dump(l,f)
					f.close()
					flag=True
					newUser()
				else:
					print("Password not long enough ")

#To setup login table in sql
def setup():
    global sqlpass
    try:
        f=open('sqlpass.dat','rb')
        l=pickle.load(f)
        sqlpass=l[0]
        f.close()
    except FileNotFoundError:
        sqlpass = getpass.getpass(prompt="Enter the password to your MySQL connection: ")
        print()
        f=open("sqlpass.dat",'wb')
        l=[sqlpass]
        pickle.dump(l,f)
        f.close()

    mydb=connector.connect(host="localhost",user="root",password=sqlpass)
    mycursor=mydb.cursor()
    mycursor.execute("create database if not exists project;")
    mycursor.execute("use project;")
    mycursor.execute("create table if not exists login(user varchar(20) not null unique primary key, password varchar(20), role varchar(20));")

#To create interface for login
def loginMenu():
	setup()
	while True:
		print("1. Login with existing ID")
		print("2. Create new ID")
		print()
		option=userinput("Enter option ")
		print()
		if option=='1':
			login()
			break
		elif option=='2':
			masterLogin()
			break
		else:
			print("Invalid choice, try again. ")

#To login
def login():
	mycursor.execute('use project;')
	mycursor.execute('select * from login;')
	if mycursor.fetchall() == []:
		print("There are no users, create one")
		print()
		masterLogin()
		exit()

	print("**** LOGIN ****")
	print()
	
	flag = False
	
	while flag == False:

		user=input("Enter user ID ")
		password=getpass.getpass(prompt="Enter Password ")
		if Empty(user) or Empty(password):
			print()
		else:
			correctUserPass = False
			mycursor.execute("use project;")
			mycursor.execute("select * from login;")

			for i in mycursor:
				if i[0]==user and i[1]==password:
					flag=True
					correctUserPass = True
			
			if correctUserPass == False:
				print("Wrong User ID or Password, please try again. ")
				print()
	else:
		
		line = ("select role from login where user= %s ")
		value = (user,)
		mycursor.execute(line,value)
		for i in mycursor:
			if i[0] == "HR":
				hrMenu()
			else:
				adminMenu()

#To create new User
def newUser():
	print("**** CREATE NEW USER ****")
	flag = False
	upper = False
	lower = False
	splChar = False
	num = False
	while flag == False:
		flag2 = True
		while flag2 == True:
			a=0
			user=userinput("Enter a username (less than 20 characters) ")
			mycursor.execute("use project;")
			mycursor.execute("select user from login;")
			for i in mycursor:
				if user.upper() == i[0].upper():
					print("Username taken, please try again")
					a=1
			if a == 0:
				flag2 = False

		#inputting password
		while True:
			print()
			password=getpass.getpass(prompt="Enter Password (less than 20 characters):")
			if len(password)>=8:
				for j in password:
					if j in string.ascii_uppercase:
						upper = True
					elif j in string.ascii_lowercase:
						lower = True
					elif j in string.punctuation:
						splChar = True
					elif j in string.digits:
						num = True
				if upper == False:
					print("Password must have uppercase letter")
				elif lower == False:
					print("Password must have lowercase letter")
				elif splChar == False:
					print("Password must have special characters")
				elif num == False:
					print("Password must have a number")
				else:
					print("Password accepted")
					break
			else:
				print("Password must be at least 8 characters long")
		print()
		while flag == False:
			role=input("HR/ ADMIN? ")
			if role == "HR" or role == "ADMIN":
				line = "insert into login values(%s,%s,%s);"
				values = (user,password,role)
				mycursor.execute(line,values)
				print("User created successfully ")
				mycursor.execute("commit;")
				login()
				flag = True
			else:
				print("Invalid Role, try again")
				print()

#Searching Based on ID number
def searching_id():

    Id_no=intInput("Enter the id number which is to be searched: ")
    mydb=connector.connect(host="localhost",user="root",password=sqlpass)
    mycursor=mydb.cursor()
    mycursor.execute("use project;")
    searchSt="select * from Associate_details where Emp_ID = %d;" %(Id_no, )
    mycursor.execute(searchSt)
    x=mycursor.fetchall()

    if x==[]:
        print("ID you are searching for does not exist!")
    else:
        for i in x:
            print("Username = ",i[1])
            print("User's Role = ",i[9])
            print("User's ID = ",i[0])
            print("User's Phone Number = ",i[5])

#Searching Based on Name
def searching_name():

    User_name=userinput("Enter the name which is to be searched: ")
    mydb=connector.connect(host="localhost",user="root",password=sqlpass)
    mycursor=mydb.cursor()
    mycursor.execute("use project;")
    search1="select * from associate_details where First_Name = \"%s\";" %(User_name, )
    mycursor.execute(search1)
    x=mycursor.fetchall()
    if x==[]:
            print("Name you are searching for does not exist")
    else:
            for i in x:
                    print("Username = ",i[1])
                    print("User's Role = ",i[9])
                    print("User's ID = ",i[0])
                    print("User's Phone Number = ",i[5])
            
#Searching Based on contact number
def searching_phone():

    User_name=userinput("Enter the id number which is to be searched: ")
    mydb=connector.connect(host="localhost",user="root",password=sqlpass)
    mycursor=mydb.cursor()
    mycursor.execute("use project;")
    search1="select * from Associate_details where Contact_Number =\"%s\";" %(User_name, )
    mycursor.execute(search1)
    x=mycursor.fetchall()

    if x==[]:
       print("The Contact number you are searching for does not exist")
    else:

        for i in x:

            print("Username = ",i[1])
            print("User's Role = ",i[9])
            print("User's ID = ",i[0])
            print("User's Phone Number = ",i[5])

#Modifying details
def modifying():
    #according to the user's names
    def exchanging_name():
        global mycursor
        mycursor.execute("select * from associate_details;")
        a = mycursor.fetchall()
        if a == []:
            print("No Row to Modify, please add values first")
            print()
        else:
            eid=intInput("Enter your id ")
            new_name=userinput("Enter the new name: ")
            mydb=connector.connect(host="localhost",user="root",password=sqlpass)
            mycursor=mydb.cursor()
            mycursor.execute("use project;")
            up="update Associate_details set First_Name = \"%s\" where Emp_id= \"%d\";" %(new_name.upper(),eid) 
            mycursor.execute(up)
            mydb.commit()
            print()
            print("Updated Values")
            print()
  


    def exchanging_dob():
        global mycursor
        mycursor.execute("select * from associate_details;")
        a = mycursor.fetchall()
        if a == []:
            print("No Row to Modify, please add values first")
            print()
        else:
            eid=intInput("Enter your id ")
            while True:
                new_date=userinput("Enter the new date of birth (YYYY-MM-DD Format): ")
                if isDate(new_date):
                    break
            mydb=connector.connect(host="localhost",user="root",password=sqlpass)
            mycursor=mydb.cursor()
            mycursor.execute("use project;")
            up="update Associate_details set DOB = \"%s\" where Emp_id= \"%d\";" %(new_date,eid) 
            mycursor.execute(up)
            mycursor.commit()
            print()
            print("Updated values")
            print()


    def exchanging_add():
        global mycursor
        mycursor.execute("select * from associate_details;")
        a = mycursor.fetchall()
        if a == []:
            print("No Row to Modify, please add values first")
            print()
        else:
            eid=intInput("Enter Employee ID: ")
            new_address=userinput("Enter the new address : ")
            mydb=connector.connect(host="localhost",user="root",password=sqlpass)
            mycursor=mydb.cursor()
            mycursor.execute("use project;")
            up="update Associate_details set Address = \"%s\" where Emp_id= \"%d\";" %(new_address.upper(),eid) 
            mycursor.execute(up)
            mydb.commit()
            print()
            print("Updated Values")
            print()      

    def exchanging_phoneno():
        global mycursor
        mycursor.execute("select * from associate_details;")
        a = mycursor.fetchall()
        if a == []:
            print("No Row to Modify, please add values first")
            print()
        else:
            eid=intInput("Enter Employee ID: ")
            new_phno=intInput("Enter the new Phone Number : ")
            mydb=connector.connect(host="localhost",user="root",password=sqlpass)
            mycursor=mydb.cursor()
            mycursor.execute("use project;")
            up="update Associate_details set Contact_Number = '%d' where Emp_id= '%d';" %(new_phno,eid)
            mycursor.execute(up)
            mydb.commit()
            print()
            print("Updated Values")
            print()


    def exchanging_dojoin():
        global mycursor
        mycursor.execute("select * from associate_details;")
        a = mycursor.fetchall()
        if a == []:
            print("No Row to Modify, please add values first")
            print()
        else:
            eid=intInput("Enter Employee ID: ")
            while True:
                new_doj=userinput("Enter the new date of joining (YYYY-MM-DD Format): ")
                if isDate(new_doj):
                    break
            mydb=connector.connect(host="localhost",user="root",password=sqlpass)
            mycursor=mydb.cursor()
            mycursor.execute("use project;")
            up="update Associate_details set Date_of_join = \"%s\" where Emp_id= '%d';" %(new_doj,eid) 
            mycursor.execute(up)
            mydb.commit()
            print()
            print("Updated Values")
            print()


    def exchanging_qual():
        global mycursor
        mycursor.execute("select * from associate_details;")
        a = mycursor.fetchall()
        if a == []:
            print("No Row to Modify, please add values first")
            print()
        else:
            eid=intInput("Enter Employee ID: ")
            new_q=userinput("Enter the new qualification: ")
            mydb=connector.connect(host="localhost",user="root",password=sqlpass)
            mycursor=mydb.cursor()
            mycursor.execute("use project;")
            up="update Associate_details set Qualification = \"%s\" where Emp_id= '%d';" %(new_q.upper(),eid) 
            mycursor.execute(up)
            mydb.commit()
            print()
            print("Updated Values")
            print()


    def exchanging_team():
        global mycursor
        mycursor.execute("select * from associate_details;")
        a = mycursor.fetchall()
        if a == []:
            print("No Row to Modify, please add values first")
            print()
        else:
            eid=intInput("Enter Employee ID: ")
            new_tem=userinput("Enter the new team: ")
            mydb=connector.connect(host="localhost",user="root",password=sqlpass)
            mycursor=mydb.cursor()
            mycursor.execute("use project;")
            up="update Associate_details set Team = \"%s\" where Emp_id= '%d';" %(new_tem.upper(),eid) 
            mycursor.execute(up)
            mydb.commit()
            print()
            print("Updated Values")
            print()

    def exchanging_Job_title():
        global mycursor
        mycursor.execute("select * from associate_details;")
        a = mycursor.fetchall()
        if a == []:
            print("No Row to Modify, please add values first")
            print()
        else:
            eid=intInput("Enter Employee ID: ")
            new_job=userinput("Enter the new Job title: ")
            mydb=connector.connect(host="localhost",user="root",password=sqlpass)
            mycursor=mydb.cursor()
            mycursor.execute("use project;")
            up="update Associate_details set Job_title = \"%s\" where Emp_id= '%d';" %(new_job.upper(),eid) 
            mycursor.execute(up)
            mydb.commit()
            print()
            print("Updated Values")
            print()


    def exchanging_status():
        global mycursor
        mycursor.execute("select * from associate_details;")
        a = mycursor.fetchall()
        if a == []:
            print("No Row to Modify, please add values first")
            print()
        else:
            eid=intInput("Enter Employee ID: ")
            new_all=userinput("Enter if allocated or unacllocated: ")
            mydb=connector.connect(host="localhost",user="root",password=sqlpass)
            mycursor=mydb.cursor()
            mycursor.execute("use project;")
            up="update Associate_details set Status = \"%s\" where Emp_id= '%d';" %(new_all.upper(),eid) 
            mycursor.execute(up)
            mydb.commit()
            print()
            print("Updated Values")
            print()


    def adding_isu():
        global mycursor
        mycursor.execute("select * from associate_details;")
        a = mycursor.fetchall()
        if a == []:
            print("No Row to Modify, please add values first")
            print()
        else:
            eid=intInput("Enter Employee ID: ")
            details_isu=userinput("Enter your ISU details : ")
            mydb=connector.connect(host="localhost",user="root",password=sqlpass)
            mycursor=mydb.cursor()
            mycursor.execute("use project;")
            up="update Associate_details set ISU = \"%s\" where Emp_id= '%d';" %(details_isu.upper(),eid) 
            mycursor.execute(up)
            mydb.commit()
            print()
            print("Updated Values")
            print()

    while True:
        print("Which do want to modify \n1)Name\n2)Date of birth\n3)Address\n4)Contact Number\n5)Date of joining\n6)Qualification\n7)Team\n8)Job Title\n9)Allocated unallocated\n10)ISU Details" )
        option=intInput(" ")
        x=[exchanging_name,exchanging_dob,exchanging_add,exchanging_phoneno,exchanging_dojoin,exchanging_qual,exchanging_team,exchanging_Job_title,exchanging_status,adding_isu]
        x[option-1]()
        print("Do you want to continue? (Type y/n)")
        x=userinput("")
        if x=="n" or x=="N":
            break

#Bigger function for modifying the job openings details
def modify_job_openings():


    def exchanging_domain():
        global mycursor
        mycursor.execute("select * from job_details;")
        a = mycursor.fetchall()
        if a == []:
            print("No Row to Modify, please add values first")
            print()
        else:
            emp=intInput("Enter the Job ID: ")
            new_domain=userinput("Enter the new domain: ")
            mydb=connector.connect(host="localhost",user="root",password=sqlpass)
            mycursor=mydb.cursor()
            mycursor.execute("use project;")
            up="update Job_details set Domain = \"%s\" where Job_id= '%d';" %(new_domain.upper(),emp) 
            mycursor.execute(up)
            mydb.commit()
            print()
            print("Updated Values")
            print()

    def exchanging_no_of_openings():
        global mycursor
        mycursor.execute("select * from job_details;")
        a = mycursor.fetchall()
        if a == []:
            print("No Row to Modify, please add values first")
            print()
        else:
            emp=intInput("Enter the Job ID: ")
            new_openings=intInput("Enter the updated number of openings :  ")
            mydb=connector.connect(host="localhost",user="root",password=sqlpass)
            mycursor=mydb.cursor()
            mycursor.execute("use project;")
            up="update Job_details set Number_of_openings = \"%d\" where Job_id= '%d';" %(new_openings,emp) 
            mycursor.execute(up)
            mydb.commit()
            print()
            print("Updated Values")
            print()

    def exchanging_tech():
        global mycursor
        mycursor.execute("select * from job_details;")
        a = mycursor.fetchall()
        if a == []:
            print("No Row to Modify, please add values first")
            print()
        else:
            emp=intInput("Enter the Job ID: ")
            new_tech=userinput("Enter the updated technology :  ")
            mydb=connector.connect(host="localhost",user="root",password=sqlpass)
            mycursor=mydb.cursor()
            mycursor.execute("use project;")
            up="update Job_details set Technology = \"%s\" where Job_id= '%d';" %(new_tech.upper(),emp) 
            mycursor.execute(up)
            mydb.commit()
            print()
            print("Updated Values")
            print()

    def exchanging_designation():
        global mycursor
        mycursor.execute("select * from job_details;")
        a = mycursor.fetchall()
        if a == []:
            print("No Row to Modify, please add values first")
            print()
        else:
            emp=intInput("Enter the Job ID: ")
            new_designation=userinput("Enter the updated designation :  ")
            mydb=connector.connect(host="localhost",user="root",password=sqlpass)
            mycursor=mydb.cursor()
            mycursor.execute("use project;")
            up="update Job_details set Designation = \"%s\" where Job_id= '%d';" %(new_designation.upper(),emp) 
            mycursor.execute(up)
            mydb.commit()
            print()
            print("Updated Values")
            print()

    def exchanging_shifts():
        global mycursor
        mycursor.execute("select * from job_details;")
        a = mycursor.fetchall()
        if a == []:
            print("No Row to Modify, please add values first")
            print()
        else:
            emp=intInput("Enter the Job ID: ")
            new_will=userinput("Willing to work in shifts?(Y/N)  ")
            mydb=connector.connect(host="localhost",user="root",password=sqlpass)
            mycursor=mydb.cursor()
            mycursor.execute("use project;")
            up="update Job_details set Willing_work_shifts = \"%s\" where Job_id= '%d';" %(new_will.upper(),emp) 
            mycursor.execute(up)
            mydb.commit()
            print()
            print("Updated Values")
            print()


    def exchanging_years_exp():
        global mycursor
        mycursor.execute("select * from job_details;")
        a = mycursor.fetchall()
        if a == []:
            print("No Row to Modify, please add values first")
            print()
        else:
            emp=intInput("Enter the Job ID: ")
            new_years_exp=intInput("No of years of experience? ")
            mydb=connector.connect(host="localhost",user="root",password=sqlpass)
            mycursor=mydb.cursor()
            mycursor.execute("use project;")
            up="update Job_details set Year_of_experience = \"%d\" where job_id= '%d';" %(new_years_exp,emp) 
            mycursor.execute(up)
            mydb.commit()
            print()
            print("Updated Values")
            print()

    
    while True:
        print("Which do want to modify \n1)Domain\n2)No of openings\n3)Technology\n4)Designation\n5)Willingness to work in shifts\n6)Years of experience" )
        option=intInput("")
        x=[exchanging_domain,exchanging_no_of_openings,exchanging_tech,exchanging_designation,exchanging_shifts,exchanging_years_exp]
        x[option-1]()
        print("Do you want to continue? (Type y/n)")
        x=userinput("")
        if x=="n" or x=="N":
            break

#Searching the jobs

#By ID
def job_searching_id():
    jid=userinput("Enter the Job ID based on which search should proceed:  ")
    mydb=connector.connect(host="localhost",user="root",password=sqlpass)
    mycursor=mydb.cursor()
    mycursor.execute("use project;")
    search1="select * from Job_details where Job_ID = \"%s\";" %(jid, )
    mycursor.execute(search1)
    x=mycursor.fetchall()
    if x==[]:
        print("None")
    else:
        for i in x:
            
            print("Job ID = ",i[0])
            print("Job Title = ",i[1])
            print("ISU = ",i[6])
            print("Job Domain = ",i[4])

#By Name
def job_searching_name():
    name=userinput("Enter the name based on which search should proceed:  ")
    mydb=connector.connect(host="localhost",user="root",password=sqlpass)
    mycursor=mydb.cursor()
    mycursor.execute("use project;")
    search1="select * from Job_details where Job_Title = \"%s\";" %(name, )
    mycursor.execute(search1)
    x=mycursor.fetchall()
    if x==[]:
        print("None")
    else:
        for i in x:
            
            print("Job ID = ",i[0])
            print("Job Title = ",i[1])
            print("ISU = ",i[6])
            print("Job Domain = ",i[4])

#Searching Based on ISU
def job_searching_isu():

    techno=userinput("Enter the ISU based on which search should proceed:  ")
    mydb=connector.connect(host="localhost",user="root",password=sqlpass)
    mycursor=mydb.cursor()
    mycursor.execute("use project;")
    search1="select * from Job_details where ISU = \"%s\";" %(techno, )
    mycursor.execute(search1)
    x=mycursor.fetchall()
    if x==[]:
        print("None")
    else:
        for i in x:
            
            print("Job ID = ",i[0])
            print("Job Title = ",i[1])
            print("ISU = ",i[6])
            print("Job Domain = ",i[4])

#Searching Based on technolgy
def job_searching_tech():

    techno=userinput("Enter the technology based on which search should proceed:  ")
    mydb=connector.connect(host="localhost",user="root",password=sqlpass)
    mycursor=mydb.cursor()
    mycursor.execute("use project;")
    search1="select * from Job_details where Technology = \"%s\";" %(techno, )
    mycursor.execute(search1)
    x=mycursor.fetchall()
    if x==[]:
        print("None")
    else:
        
        for i in x:
            print("Job ID = ",i[0])
            print("Job Title = ",i[1])
            print("ISU = ",i[6])
            print("Job Domain = ",i[4])

#The main menu for HR
def mainMenu():
    while True:
        print()
        print("1.Adding a new associate")
        print("2.Searching for an associate")
        print("3.Modifying associate details")
        print("4.Removing an associate")
        print("5.Add Job Details")
        print("6.Generate Report")
        print("7.Modify Job Openings")
        print("8.Searching Job Openings")
        print("9.Exit")
        print()
        ch=intInput("Enter the choice ")
        print()
        if ch==1:
            add()
        elif ch==2:
            print("A. Search by Employee ID")
            print("B. Search by Name")
            print("C. Search by Contact Number")
            while True:
                choice = userinput("Enter option: ")
                print()
                if choice.upper() == "A":
                    searching_id()
                    break
                elif choice.upper() == "B":
                    searching_name()
                    break
                elif choice.upper() == "C":
                    searching_phone()
                    break
                else:
                    print("Wrong Input try again")
        elif  ch==3:
            modifying()
        elif ch==4:
            to_remove()
        elif ch==5:
            addjob()
        elif ch==6:
            print("A. REPORT ON UNALLOCATED JOBS")
            print("B. REPORT ON JOBS WITH ISU DETAILS")
            print("C. REPORT ON ISU DETAILS")
            a = userinput("Type your choice: ")
            if a.upper() == 'A':
                Unallocated_Report()
            elif a.upper() == 'B':
                JobISU_Report()
            elif a.upper() == "C":
                isuReport()
            else:
                print("Invalid Option try again")
        elif ch==7:
            modify_job_openings()
        elif ch==8:
            print()
            print("A.Job ID")
            print("B.Job Name")
            print("C.ISU")
            print("D.Tech")
            print()
            choice = userinput("Enter the criteria you want to search on: ")
            print()
            if choice.upper() == "A":
                job_searching_id()
            elif choice.upper() == "B":
                job_searching_name()
            elif choice.upper() =="C":
                job_searching_isu()
            elif choice.upper() == "D":
                job_searching_tech()
        elif ch == 9:
            print("SEE YOU NEXT TIME!")
            break
        else:
            print("Invalid option, try again")


#Function to add associate details
def add():
    mycursor.execute('use project;')
    mycursor.execute("create table if not exists Associate_Details(Emp_ID varchar(20) not null unique primary key,First_name varchar(15), Gender varchar(5),DOB date,Address varchar(30),Contact_number varchar(10),Date_of_join date, Qualification varchar(10),Team varchar(10),Job_title varchar(15),Status varchar(12),ISU varchar(50));")
    mycursor.execute("commit;")

    Flag = True
    print("**** CREATE NEW ASSOCIATE ****")
    print()
    while Flag == True:
        c=0
        while True:
            j=0
            emp = intInput("Enter the Employee ID: ")
            mycursor.execute("select Emp_ID from Associate_details;")
            for i in mycursor:
                if int(i[0])==emp:
                    print()
                    print("ID ALREADY TAKEN, TRY AGAIN")
                    print()
                    j+=1
            if j == 0:
                break
        fname = userinput("Enter the first name: ")
        gen = userinput("Enter the Gender M/F: ")
        a = True
        while a == True:
            dob = userinput("Enter the date of birth (YYYY-MM-DD): ")
            if isDate(dob):
                if dob > '2003-01-01':
                    print("Must be an adult, try again ")
                    continue
                else:
                    a = False
            else:
                a = True
        Address = userinput("Enter the address: ")
        h = True
        while h == True:
            while True:
                j=0
                contactno = userinput("Enter the Phone number: ")
                mycursor.execute("select Contact_number from Associate_details;")
                for i in mycursor:
                    if int(i[0])==int(contactno):
                        print()
                        print("PHONE NO. ALREADY TAKEN, TRY AGAIN")
                        print()
                        j+=1
                    if j == 0:
                        break
            if contactno.isdigit() and len(contactno) == 10:
                h=False
            else:
                print("Re-enter the contact number, no alphabets allowed and lenght must be 10")
                continue
        while True:
            Dateofjoin = userinput("Enter the date of joining(YYYY-MM-DD): ")
            if isDate(Dateofjoin):
                break
        qualification = userinput("Enter the Qualification: ")
        team = userinput("Enter the team: ")
        job = userinput("Enter the Job title: ")
        while True:
            status = userinput('Enter the status (ALLOCATED/UNALLOCATED): ')
            if status.upper() != "ALLOCATED" or status.upper() != "UNALLOCATED":
                print("MUST ONLY INPUT 'ALLOCATED' OR 'UNALLOCATED'")
                print()
        isu = userinput("Enter ISU details: ")
        c+=1
        l = "insert into Associate_Details values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        v=(emp,fname.upper(),gen.upper(),dob,Address.upper(),contactno,Dateofjoin,qualification.upper(),team.upper(),job.upper(),status.upper(),isu.upper())
        mycursor.execute(l,v)
        mycursor.execute("commit;")
        print("DATA ADDED")
        while True:
            ch = userinput("DO YOU WANT TO  ADD MORE RECORDS?(Y/N)")
            if ch.upper() == "N" or ch.upper() == "Y":
                if ch.upper() == "N":
                    print("Back to Main Menu")
                    print()
                    break
            else:
                print("Invalid choice, try again")
                print()

#Funtion to remove associate
def to_remove():
    mycursor.execute("use project;")
    mycursor.execute("select * from associate_details;")
    a = mycursor.fetchall()
    if a == []:
        print("No Associate to delete, input values first")
        print()
    else:
        ID = userinput("Enter the Emp_ID of the associate to be deleted: ")
        mycursor.execute("delete from associate_details where Emp_ID=%s"%(ID,))
        mycursor.execute("commit;")
        print("ROW DELETED")

#To add a job opening
def addjob():
	mydb = connector.connect(host='localhost',user="root",password=sqlpass)
	mycursor = mydb.cursor()
	mycursor.execute('use project;')
	mycursor.execute("create table if not exists Job_Details(Job_ID int(3) not null unique primary key, Job_Title varchar(50),Number_of_openings int(10), Year_of_experience int(2),Domain varchar(20),Technology varchar(30),ISU varchar(50),Willing_work_shifts varchar(3),Designation varchar(20));")
        
	mydb.commit()
        
	Flag = True
	print("Please enter the required information")
	c = 0
	while Flag == True:
		while True:
			j=0
			emp = intInput("Enter the Job ID: ")
			mycursor.execute("select Job_ID from Job_Details;")
			for i in mycursor:
				if i[0]==emp:
					print()
					print("ID ALREADY TAKEN, TRY AGAIN")
					print()
					j+=1
			if j == 0:
				break
		name = userinput("Enter the Job Title: ")
		nopenings = intInput("Enter the number of openings: ")
		yrsxp = intInput("Enter the years of experience: ")
		Domain= userinput("Enter domain: ")
		Tech = userinput("Enter technology: ")
		ISU = userinput("Enter ISU Details: ")
		shifts = userinput("Shifts? YES / NO: ")
		Designation = userinput("Enter Designation ")
            
            
		l="insert into Job_Details values(%s,%s,%s,%s,%s,%s,%s,%s,%s);"
		v=(emp,name.upper(),nopenings,yrsxp,Domain.upper(),Tech.upper(),ISU.upper(),shifts.upper(),Designation.upper())
		mycursor.execute(l,v)
		mydb.commit()
		c+=1
		print("DATA ADDED")
		ch=userinput("DO YOU WANT TO  ADD MORE RECORDS?(Y/N)")
		if ch=='N' or ch=='n':
			if c==1:
 				print("You Have entered 1 record")
			else:
				print("YOU HAVE ENTERED",c,"RECORDS")
			Flag=False

#To produce Unallocated Report
def Unallocated_Report():
    mycursor.execute("use project;")
    sql = "select Emp_ID, First_Name, Contact_Number, Team, Job_Title, Status from Associate_details where Status = 'UNALLOCATED';"
    mycursor.execute(sql)
    l=list()
    l=[["EMP ID","NAME","NUMBER","TEAM","TITLE","STATUS"]]
    for i in mycursor:
        l.append(i)
    table = tabulate(l)
    with open("Unallocated Report.txt",'w') as f:
        f.writelines(table)
    print()
    print("****CREATED REPORT 'UNALLOCATED.TXT'****")
    print()

#To Produce Job ISU Report
def JobISU_Report():
    mycursor.execute('use project;')
    sql = 'select Job_ID, Job_Title, Number_of_openings, ISU from Job_details;'
    l=[["JOB ID", "JOB TITLE", "NO. OF OPENINGS", "ISU"]]
    mycursor.execute(sql)
    for i in mycursor:
        l.append(i)
    table = tabulate(l)
    with open("Job ISU.txt","w") as f:
        f.writelines(table)
    print()
    print("****CREATED REPORT 'JOB ISU.txt'****")
    print()

#To Produce a report with all the ISU details
def isuReport():
    mycursor.execute('use project;')
    sql = 'select Emp_ID, First_name, Team, ISU from Associate_Details;'
    l=[["EMP ID","NAME","TEAM","ISU DETAILS"]]
    mycursor.execute(sql)
    for i in mycursor:
        l.append(i)
    table = tabulate(l)
    with open("ISU DETAILS.txt","w") as f:
        f.writelines(table)
    print()
    print("****CREATED REPORT 'ISU DETAILS.txt'****")
    print()

#Once logged in as HR
def hrMenu():
	print("Logged in as a HR")
	mainMenu()

#Once logged in as ADMIN
def adminMenu():
    while True:
        print("Logged in as ADMIN")
        print("A. Search by Employee ID")
        print("B. Search by Employee by Name")
        print("C. Search by Employee by Contact Number")
        print("D. Generate Reports")
        print("Type 'Exit' to quit")
        choice = userinput("Enter option: ")
        if choice.upper() == "A":
            searching_id()
        elif choice.upper() == "B":
            searching_name()
        elif choice.upper() == "C":
            searching_phone()
        elif choice.upper() == "D":
            print("A. REPORT ON UNALLOCATED JOBS")
            print("B. REPORT ON JOBS WITH ISU DETAILS")
            print("C. REPORT ON ISU DETAILS")
            a = userinput("Type your choice: ")
            if a.upper() == 'A':
                Unallocated_Report()
            elif a.upper() == 'B':
                JobISU_Report()
            elif a.upper() == "C":
                isuReport()
            else:
                print("Invalid Option try again")
        elif choice.upper() == "EXIT":
            print("Session over")
            break
        else:
            print("Wrong Input try again")
            print()

#MAIN CODE:
setup()
mydb=connector.connect(host="localhost",user="root",password=sqlpass)
mycursor=mydb.cursor()

loginMenu()












