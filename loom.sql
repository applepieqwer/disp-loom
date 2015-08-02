PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE "datelines" (
  "iddatelines" date NOT NULL,
  "d_is_holiday" tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY ("iddatelines")
);
INSERT INTO "datelines" VALUES('2012-01-25',0);
INSERT INTO "datelines" VALUES('2012-01-26',0);
INSERT INTO "datelines" VALUES('2012-01-27',0);
INSERT INTO "datelines" VALUES('2012-01-28',0);
INSERT INTO "datelines" VALUES('2012-01-29',0);
INSERT INTO "datelines" VALUES('2012-01-30',0);
INSERT INTO "datelines" VALUES('2012-01-31',0);
INSERT INTO "datelines" VALUES('2012-02-01',0);
INSERT INTO "datelines" VALUES('2012-02-02',0);
INSERT INTO "datelines" VALUES('2012-02-03',0);
INSERT INTO "datelines" VALUES('2012-02-04',0);
INSERT INTO "datelines" VALUES('2012-02-05',0);
INSERT INTO "datelines" VALUES('2012-02-06',0);
INSERT INTO "datelines" VALUES('2012-02-07',0);
INSERT INTO "datelines" VALUES('2012-02-08',0);
INSERT INTO "datelines" VALUES('2012-02-09',0);
INSERT INTO "datelines" VALUES('2012-02-10',0);
INSERT INTO "datelines" VALUES('2012-02-11',0);
INSERT INTO "datelines" VALUES('2012-02-12',0);
INSERT INTO "datelines" VALUES('2012-02-13',0);
INSERT INTO "datelines" VALUES('2012-02-14',0);
INSERT INTO "datelines" VALUES('2012-02-15',0);
INSERT INTO "datelines" VALUES('2012-02-16',0);
INSERT INTO "datelines" VALUES('2012-02-17',0);
INSERT INTO "datelines" VALUES('2012-02-18',0);
INSERT INTO "datelines" VALUES('2012-02-19',0);
INSERT INTO "datelines" VALUES('2012-02-20',0);
INSERT INTO "datelines" VALUES('2012-02-21',0);
INSERT INTO "datelines" VALUES('2012-02-22',0);
INSERT INTO "datelines" VALUES('2012-02-23',0);
INSERT INTO "datelines" VALUES('2012-02-24',0);
INSERT INTO "datelines" VALUES('2012-02-25',0);
INSERT INTO "datelines" VALUES('2012-02-26',0);
INSERT INTO "datelines" VALUES('2012-02-27',0);
INSERT INTO "datelines" VALUES('2012-02-28',0);
INSERT INTO "datelines" VALUES('2012-02-29',0);
CREATE TABLE "loomitem" (
  "datelines_iddatelines" date NOT NULL,
  "tables_idtables" int(11) NOT NULL,
  "workers_idworkers" int(11) NOT NULL,
  "l_color" varchar(45) DEFAULT NULL,
  PRIMARY KEY ("datelines_iddatelines","tables_idtables","workers_idworkers")
);
CREATE TABLE "tables" (
  "idtables" INTEGER PRIMARY KEY AUTOINCREMENT,
  "t_name" varchar(45) NOT NULL,
  "t_open" time NOT NULL,
  "t_close" time NOT NULL,
  "t_can_empty" tinyint(1) NOT NULL DEFAULT '0',
  "t_disp_rule" tinyint(1) NOT NULL DEFAULT '1',
  "t_order" int(11) NOT NULL DEFAULT '10'
);
INSERT INTO "tables" VALUES(1,'签派带班','08:30:00','32:45:00',0,0,10);
INSERT INTO "tables" VALUES(2,'7010中班','13:00:00','22:10:00',0,1,10);
INSERT INTO "tables" VALUES(3,'7018中班','13:00:00','22:10:00',0,1,10);
INSERT INTO "tables" VALUES(4,'7010早班','06:10:00','13:10:00',0,1,10);
INSERT INTO "tables" VALUES(5,'7018早班','06:10:00','13:10:00',0,1,10);
INSERT INTO "tables" VALUES(6,'7018守夜','22:00:00','30:20:00',0,1,10);
INSERT INTO "tables" VALUES(7,'7018备份','22:00:00','30:20:00',1,1,10);
CREATE TABLE "workers" (
  "idworkers" INTEGER PRIMARY KEY AUTOINCREMENT,
  "w_name" varchar(45) NOT NULL,
  "w_color" varchar(45) NOT NULL
);
INSERT INTO "workers" VALUES(1,'程序','#3299CC');
CREATE TABLE "workers_limit_tables" (
  "workers_idworkers" int(11) NOT NULL,
  "tables_idtables" int(11) NOT NULL,
  PRIMARY KEY ("workers_idworkers","tables_idtables")
);
INSERT INTO "workers_limit_tables" VALUES(1,1);
INSERT INTO "workers_limit_tables" VALUES(1,2);
INSERT INTO "workers_limit_tables" VALUES(1,4);
INSERT INTO "workers_limit_tables" VALUES(1,5);
INSERT INTO "workers_limit_tables" VALUES(1,6);
INSERT INTO "workers_limit_tables" VALUES(1,7);
INSERT INTO "workers_limit_tables" VALUES(1,3);
CREATE TABLE "workers_tempo_limit" (
  "workers_idworkers" int(11) NOT NULL,
  "wtl_from" datetime NOT NULL,
  "wtl_to" datetime NOT NULL,
  "wtl_reason" varchar(45) DEFAULT NULL,
  PRIMARY KEY ("workers_idworkers")
);
CREATE INDEX "workers_limit_tables_fk_workers_has_tables_workers_idx" ON "workers_limit_tables" ("workers_idworkers");
COMMIT;
