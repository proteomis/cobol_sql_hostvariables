For those who find it tedious to manually generate the SQL table declarations, COBOL host variables, and COBOL indicator variables required to use embedded SQL for COBOL, here is a small Python script that does the job, at least the basics.
The script is designed for Postgresql databases.
It connects to a database, retrieves the list of tables, and for each table, it creates a cpy file containing the declarations.
All that remains is to specify the file in the WSS.

        working-storage section.
        exec sql begin declare section end-exec.
          copy "mytable1.cpy".
          copy "mytable2.cpy".
          copy "sqlca.cpy".
        exec sql end declare section end-exec.

where mytable1.cpy is for example:

        *> -------------------------------------------
        *> DECLARE TABLE for mytable1.
        *> -------------------------------------------
         EXEC SQL DECLARE mytable1 TABLE
         (
            code               bpchar(15)           NOT NULL
          , libelle            varchar(270)         
         ) END-EXEC.
        *> -------------------------------------------
        *> COBOL HOST VARIABLES FOR TABLE mytable1.
        *> -------------------------------------------
         01  DCLmytable1.
           03 mytable1-code               pic x(15).
           03 mytable1-libelle            pic x(270).
        *> -------------------------------------------
        *> COBOL INDICATOR VARIABLES FOR TABLE mytable1.
        *> -------------------------------------------
         01  DCLmytable1.-NULL.
           03 mytable1-code-NULL pic s9(04) comp-5.
           03 mytable1-libelleen-NULL pic s9(04) comp-5.
        *>----- End of file

Here is the syntax:

    usage: cblsql4pg.py [-h] -d DATABASE -u USER -p PASSWORD [-H HOST] [-P PORT]
    
    Generate COBOL declarations from PostgreSQL database tables.
    options:
      -h, --help            show this help message and exit
      -d DATABASE, --database DATABASE
                            Database name
      -u USER, --user USER  Database user
      -p PASSWORD, --password PASSWORD
                            Database password
      -H HOST, --host HOST  Database host
      -P PORT, --port PORT  Database port


