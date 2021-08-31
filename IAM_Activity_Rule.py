import boto3 
from datetime import *
import json

# Declare IAM and SNS as the boto3 clients for this lambda function
iam = boto3.client('iam')
sns = boto3.client('sns')

# Function for lambda begins here
def lambda_handler(event, context):
    
    # Everything will start from here
    role_list = iam.list_roles()
    

    # Terminal output of number of roles presently active in the account
    var = str(len(role_list['Roles']))
    print("There are " + var + " roles in this account.")
    print("\n     ")
    
    
    # Create empty array and pass role_list results to array
    list_of_roles = []
    
    for role in role_list['Roles']:
        list_of_roles.append(role['RoleName'])
        #print(role['RoleName'])
    
    
    # Will contain results of get_role iteration  
    got_roles = []
    
    # Getting role names and passing them to get_role() method
    for r in list_of_roles:
        get_role = iam.get_role(RoleName=r)
        got_role = get_role['Role']['RoleLastUsed']
        
        
        if 'LastUsedDate' in got_role:
            got_roles.append(json.dumps(got_role['LastUsedDate'], default=str))
        
    
    # Empty dictionary where list items that have been placed into k:v pairs will be stored
    temp_dict = {}
    
    # Loop through list_of_roles and got_roles timestamps then output them as k:v pairs
    for x, y in zip(list_of_roles, got_roles):
        temp_dict[x]=y
    
    
    # Converting datetime strings to datetime objects using a dictionary comprehension and strptime() method
    output_dict = {k:v.strip('"') for (k,v) in temp_dict.items()}
    output_dict = {k:datetime.strptime(v, "%Y-%m-%d %H:%M:%S%z") for (k,v) in output_dict.items()}
    
    
    """Now begins the datetime object comparison logic section of the lambda function."""
    # Creating today variable by which role datetime objects will be compared to 
    present_day = datetime.now(timezone.utc)
    
    # Define the length of days to evaluate compliance or non compliance 
    td_3  = timedelta(days=3)
    td_5  = timedelta(days=5)
    td_7  = timedelta(days=7)
    
    # Passing delta specifications to a list
    delta_list = td_3, td_5, td_7
    
    # Dictionary of delta values of 
    diff = {k:present_day - v for (k,v) in output_dict.items()}
    
    # Empty list to which loop result will be passed
    non_comp_email = []
    
    for k, v in diff.items():
        if v < td_3:
                compliant = k + ' is: COMPLIANT'
        elif v > td_7:
            non_comp_dict = {k:str(v)}
            for k, v in non_comp_dict.items():
                non_comp_email.append(k + " is non compliant as of: " + v)
        elif v > td_5:
            non_comp_dict = {k:str(v)}
            for k, v in non_comp_dict.items():
                non_comp_email.append(k + " is non compliant as of: " + v)
        elif v > td_3:
            non_comp_dict = {k:str(v)}
            for k, v in non_comp_dict.items():
                non_comp_email.append(k + " is non compliant as of: " + v)
    
    # For terminal output only
    for x in non_comp_email:
        test = print(str(x), end = "\n")

    
    
    # SNS notification to be sent out if roles are found non-compliant
    response = sns.publish(TopicArn={aws_sns_arn}, Message=json.dumps(non_comp_email), Subject="Unused IAM Role Report")
    
    return {
        'status': 200,
        'message': response,
        }
