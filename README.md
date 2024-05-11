# ptstart_bot
This project is made for PT-START internship. It's a telegram bot that:

connects to remote ssh server, can get some information from there
can search for numbers, for emails, write them to postgresql databases
verifies your password strength I hope that you'll like it )

### ansible branch
Use it if you want to deploy a project by ansible blaybook.
Download ansible on your PC, create a user and add it to /etc/sudoers (Example: ansible ALL(ALL:ALL) NOPASSWD:ALL), same on all hosts
Edit the inventory file, put the ip addresses of your machines.
Enable ssh service on db_image machine. 
Edit the env.txt file, put the required ip addresses. Important: RM_HOST address must match DB_HOST to get replication logs.
Check the available versions of postgresql on your PC. If necessary, replace the paths in postgresql_master.conf, postgresql_slave.conf and playbook_tg_bot. 
Example: if you can install postgresql version 12 on your PC, the paths should start with etc/postgresql/12..... Etc.
You will also need to replace the line in the bot.py file after loading the repository in the GetReplLogs function with a link to the log file in the same way.
If the user cloning does not run initially - give permissions to the ansible user on the /ansible/ptstart_bot folder
If the bot cloning will not run again - clean up the /ansible/ptstart_bot folder

### docker branch
Download docker, docker-compose to your pc.
Download the repository
In the devops_bot/bot folder add the .env file . You can find an example file in the ansible branch.
Start an ssh service on the host machine, access it as a remote ssh server if you want to get replication logs.
On my PC docker was started by docker compose up command.
