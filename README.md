# ptstart_bot
This project is made for PT-START internship. It's a telegram bot that:

connects to remote ssh server, can get some information from there
can search for numbers, for emails, write them to postgresql databases
verifies your password strength I hope that you'll like it )

### ansible branch
Use it if you want to deploy a project by ansible blaybook.<br/>
Download ansible on your PC, create a user and add it to /etc/sudoers (Example: ansible ALL(ALL:ALL) NOPASSWD:ALL), same on all hosts<br/>
Edit the inventory file, put the ip addresses of your machines.<br/>
Enable ssh service on db_image machine. <br/>
Edit the env.txt file, put the required ip addresses. Important: RM_HOST address must match DB_HOST to get replication logs.<br/>
Check the available versions of postgresql on your PC. If necessary, replace the paths in postgresql_master.conf, postgresql_slave.conf and playbook_tg_bot. <br/>
Example: if you can install postgresql version 12 on your PC, the paths should start with etc/postgresql/12..... Etc.<br/>
You will also need to replace the line in the bot.py file after loading the repository in the GetReplLogs function with a link to the log file in the same way.<br/>
If the user cloning does not run initially - give permissions to the ansible user on the /ansible/ptstart_bot folder<br/>
If the bot cloning will not run again - clean up the /ansible/ptstart_bot folder<br/>

### docker branch
Download docker, docker-compose to your pc.<br/>
Download the repository<br/>
In the devops_bot/bot folder add the .env file . You can find an example file in the ansible branch.<br/>
Start an ssh service on the host machine, access it as a remote ssh server if you want to get replication logs.<br/>
On my PC docker was started by docker compose up command.<br/>
