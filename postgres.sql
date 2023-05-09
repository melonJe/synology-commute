CREATE TABLE "commute" (
  "employee_id" int(11) DEFAULT NULL,
  "date" date DEFAULT NULL,
  "come_at" time DEFAULT NULL,
  "leave_at" time DEFAULT NULL
);

CREATE TABLE "employee" (
  "employee_id" int(11) DEFAULT NULL,
  "name" varchar(100) DEFAULT NULL,
  "manager" tinyint(1) DEFAULT '0'
);
