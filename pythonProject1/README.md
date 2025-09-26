# S3 Object Store
## Overview
This is a Flask application that runs locally with a sqlite db. 
The intention is to be a rough proof of concept for a web app that
will allow users to set up organization-based accounts to manage various asset files. 
There are three different role types expected at this time:
1. Admin
2. Editor
3. Viewer

## Why this implementation
If I was truly tasked with a spike ticket, and needed a relevant work sample, 
id like it to demonstrate the most important aspects of the requirements. In this case, 
the three most clearly identified AC to me were:

1. Upload files 
2. Role based access
3. SRE (Admin) level access (while not fully built out, the concept and template differentiation are there)

I chose to construct this because it was the barest MVP that I felt displayed all three. 
It allows users of varying access levels to log into the app and access content, experience 
displays pertinant to their role, and allows the appropriate role (Editor for now) to successfully
upload objects to an S3 bucket in the cloud.

I suppose I could have left out the whole register and login page and just manually set
credentials and demoed but it fit in nicely with what I already planned to build so i 
went with it. 

## Considerations & Assumptions
1. I made some assumptions around user journey outcomes. Namely that for now it would be fine to have more constrained user roles (just can i upload or can i view only?). That might not be sufficient coming out of a full discovery session, but my hope was that the user roles could be built upon later to allow a more component or feature specific access.
2. I approached this from a UI first standpoint. I think ultimately a CLI would provide more light weight access for SREs, however, OOTB if we are constructing the back end capabilities to do our MVP requirements, given the lightness of what I imagine the UI being at first, it would require less work to just integrate it into the app that way. This initial implementation would also allow people who may not necessarily be SRE level to act in a customer support role. 

## Next Few Improvements
1. Clean up and modularize directory
2. Complete the Admin dashboard
3. Add test cases for:
   1. DB connectivity
   2. AWS connectivity
   3. File type variation in uploads
4. Add delete capabilities
5. Construct a ticketing interface 

----------------------------------------

## What was accomplished
* Create scaffold UI of most basic content for user editor and viewer user flow.
  * User registration
  * User login
  * File Upload ( Editors only )
  * Uploaded file viewing
* Laid out unfinished static dashboard for SREs (admins)
* Leverages RBAC to determine what content users have access to
* Establish connection to external AWS account that allows access to manage S3

## How to set some of this up yourself
This app connects to an AWS account by means of local profile configuration. 
You will need to do the following to connect it yourself:
1. Ensure your bucket permissions are configured as desired. You can make this as secure or insecure as you'd like but you may need to modify the permissions on your user or role accordingly.
2. Create a user or role with the [AmazonS3FullAccess](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonS3FullAccess.html) permission policy
   3. Option to create temporary access keys for a simpler approach
3. [Configure your profile](https://docs.aws.amazon.com/cli/latest/reference/configure/) on your local machine
4. If you are having trouble with permissions, make sure that the profile boto is picking up is the one you want. If you don't specifically declare it, it will use the default profile which may not be your intent.
5. Make sure you install the required packages and start your flask app locally. 
6. Be sure to also initialize the db via a db.create_all(). This is using sql_alchemy so you should be able to just run this once in the flask shell.

## Outstanding TODOs
This is just a list of things that I would have liked to have gotten done for this iteration. 
For a full list of other enhancements, see the solution design document.

1. Code cleanup .... I did none of it. I dumped everything in one spot because admittedly that is how I start things for a spike. I wouldn't intend for this to be the true baseline, but more like inspiration or something to react to.   
   2. Breaking out models & form funcitonality into their own directories
2. Automatically prefix uploads into folders identified by organizaiton name
3. Make admin dashboard actually pull real data
   4. More thought needs to be put into the UX of the admin page because it can be constructed in a number of ways. I was thinking a tabbed dashboard view that alternated betweeen orgs and users but we could talk through that more later because im running out of time. 
   5. Pull in all users and their metatdata
   6. Pull in all orgs
   7. Allow admins to see logs and communicate back and forth with users.