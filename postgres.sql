CREATE TABLE "commute" (
  "no" serial,
  "employee_id" int8,
  "date" date DEFAULT NULL,
  "come_at" time DEFAULT NULL,
  "leave_at" time DEFAULT NULL
);

CREATE TABLE "employee" (
  "employee_id" int8 DEFAULT NULL,
  "name" varchar(100) DEFAULT NULL,
  "manager" boolean DEFAULT '0'
);