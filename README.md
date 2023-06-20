# Real-time-object-detection-and-storage-web-application-for-security-system
you have to create a data base for this project here i give my data base structure for the reference


create database od;

use  od;

create table detected_objects (id int auto_increment primary key,label varchar(200),x1 int, y1 int, x2 int, y2 int,timestamp Timestamp DEFAULT CURRENT_TIMESTAMP);
