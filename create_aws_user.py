import boto3
import subprocess
import csv
import os
import argparse

# Create AWS user
# By https://binarydreams.biz
# Code written for Python 3.x

# Set the arguments
parser = argparse.ArgumentParser(description='Create an AWS CloudFormation user.')
parser.add_argument('-e', '--executing-profile', dest='executingprofile', default='cloudguru',
                    help='The AWS profile to use to create the new user')
parser.add_argument('-n', '--new-user', dest='newuser', default='sls-user',
                    help='The new AWS user to be created')
args = parser.parse_args()

# Use the AWS profile for this session
session = boto3.Session(profile_name=args.executingprofile)
iam = session.client('iam')

print("Create the new user")
userCreated = iam.create_user(
    UserName=args.newuser)
#print(userCreated)

print("Attach the policy to the new user")
iam.attach_user_policy(
    UserName=args.newuser, 
    PolicyArn='arn:aws:iam::aws:policy/AdministratorAccess')

print("Create the users' secret access key")
accessKey = iam.create_access_key(
    UserName=args.newuser,
)
#print(accessKey)
newUserId = accessKey['AccessKey']['AccessKeyId']
secretAccessKey = accessKey['AccessKey']['SecretAccessKey']

print("Save the AWS credentials to a CSV file")
# Note that this is a much more effective and trouble-free way of getting the new credentials
# into the AWS credentials file.
credentials_file = "credentials.csv"

with open(credentials_file, mode='w', newline='') as csv_file:
    fieldnames = ['User name', 'Access key ID', 'Secret access key']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerow({'User name': args.newuser, 'Access key ID': newUserId, 'Secret access key': secretAccessKey})

print(f"Import the temporary AWS {credentials_file}")
subprocess.run(['aws', 'configure', 'import', '--csv', f'file://{credentials_file}'])

print("Delete temporary credentials file")
os.remove(credentials_file) 