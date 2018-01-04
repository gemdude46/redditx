#!/usr/bin/env bash

log=log

while true; do
	echo '===== Starting RedditXBot =====' >> $log
	echo -n 'Time: ' >> $log
	date >> $log

	./app.py &>> $log

	echo "Exited with status code $?" >> $log
	echo 'Rebooting in 5...' >> $log
	sleep 1
	echo 'Rebooting in 4...' >> $log
	sleep 1
	echo 'Rebooting in 3...' >> $log
	sleep 1
	echo 'Rebooting in 2...' >> $log
	sleep 1
	echo 'Rebooting in 1...' >> $log
	sleep 1
	echo 'Rebooting!' >> $log
done
