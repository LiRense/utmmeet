import pymssql

def add_tables():
    server = '127.0.0.1'
    database = 'bark'
    username = 'sa'
    password = '_V0cabular'


    conn = pymssql.connect(server=server, user=username, password=password, database=database)
    cursor = conn.cursor()

    drop_tables_my = '''
    DROP TABLE bark.dbo.balance_030000434308;

    DROP TABLE bark.dbo.barcodes_030000434308;

    DROP TABLE bark.dbo.fsm_030000434308;
    '''

    create_table_fsm = '''
    CREATE TABLE fsm_030000434308 (
        id INT IDENTITY(1,1) PRIMARY KEY,
        rangeid INT NULL,
        value NVARCHAR(150) NOT NULL,
        CONSTRAINT fsm_030000434308_rangeid_fkey FOREIGN KEY (rangeid) REFERENCES ranges(id)
    );
    '''

    create_index_fsm = '''
    CREATE UNIQUE INDEX fsm_030000434308_value_uq ON fsm_030000434308 (value);
    '''

    create_table_barcodes = '''
    CREATE TABLE barcodes_030000434308 (
        id INT IDENTITY(1,1) PRIMARY KEY,
        code NVARCHAR(1024) NOT NULL,
        val NVARCHAR(150) NOT NULL,
        shard_id INT DEFAULT 0 NOT NULL,
        CONSTRAINT barcodes_030000434308_code_key UNIQUE (code)
    );
    '''

    create_index_barcodes = '''
    CREATE INDEX barcodes_030000434308_idx ON barcodes_030000434308 (code);
    '''

    create_table_balance = '''
    CREATE TABLE balance_030000434308 (
        id INT IDENTITY(1,1) PRIMARY KEY,
        code NVARCHAR(255) NOT NULL,
        val NVARCHAR(255) NOT NULL,
        shard_id INT DEFAULT 0 NOT NULL,
        CONSTRAINT balance_030000434308_code_key UNIQUE (code)
    );
    '''

    create_index_balance = '''
    CREATE INDEX balance_030000434308_ix ON balance_030000434308 (code);
    CREATE INDEX balance_030000434308_val ON balance_030000434308 (val);
    '''

    # Define the SQL commands to insert data
    insert_balance_1 = '''
    INSERT INTO balance_030000434308 (code, val, shard_id)
    VALUES ('200213539562110924001SDSOOVC0XFFI9VOIW6PY6XMJ2CRX2S2ZPWCZNWV1ADKDL4J8E3JF5SW1UI2D9251SYDJIRYSRF1J4FK17HEYKOUU4XKS7HNMBZV7SANJZARN8F07S6NVLTE4NC5APHYH1', 'TEST-FB-000000041001590', 0);
    '''

    insert_balance_3 = '''
    INSERT INTO balance_030000434308 (code, val, shard_id)
    VALUES ('200200005578581124001KWP3TLOVES8ADKMLWBE7G6QZMJU4CXYIAFZHFALRJZLS0GBOWONBUVXSX6ZCUA9TVMDEW5RNCAOQEH6X7QC1IJPGAUPD3KBFFNRYW0VNBLMG0AQT37SO5HGR9SMODPBDZ', 'TEST-FB-000000041001590', 0);
    '''

    insert_balance_2 = '''
    INSERT INTO balance_030000434308 (code, val, shard_id)
    VALUES ('22N2A1YNWKZ8GSH084U411070010000010844KNRCGUGXBZ4KAEZCS9WUQ1A0EBFY6TI', 'TEST-FB-000000041001481', 0);
    '''

    insert_balance_4 = '''
    INSERT INTO balance_030000434308 (code, val, shard_id)
    VALUES ('22N2A1YNWKZ8GSH084U411070010000011129GEKMQNZFW8C5ES0UV4GJNRIUFT2LCP9', 'TEST-FB-000000041001481', 0);
    '''

    insert_exit_barcodes_1 = '''
    INSERT INTO barcodes322
    (code, val)
    VALUES('22N2A1YNWKZ8GSH084U411070010000011129GEKMQNZFW8C5ES0UV4GJNRIUFT2LCP9', 'b62664dc66a5bcb1d6dec3c535606ff1:030000434308:42:2023-08-08::');
    '''

    insert_exit_barcodes_2 = '''
    INSERT INTO barcodes322
    (code, val)
    VALUES('22N2A1YNWKZ8GSH084U411070010000010844KNRCGUGXBZ4KAEZCS9WUQ1A0EBFY6TI', 'b62664dc66a5bcb1d6dec3c535606ff2:030000434308:42:2023-08-08::');
    '''

    insert_exit_barcodes_3 = '''
    INSERT INTO barcodes322
    (code, val)
    VALUES('200200005578581124001KWP3TLOVES8ADKMLWBE7G6QZMJU4CXYIAFZHFALRJZLS0GBOWONBUVXSX6ZCUA9TVMDEW5RNCAOQEH6X7QC1IJPGAUPD3KBFFNRYW0VNBLMG0AQT37SO5HGR9SMODPBDZ', 'b62664dc66a5bcb1d6dec3c535606ff3:030000434308:42:2023-08-08::');
    '''

    insert_exit_barcodes_4 = '''
    INSERT INTO barcodes322
    (code, val)
    VALUES('200213539562110924001SDSOOVC0XFFI9VOIW6PY6XMJ2CRX2S2ZPWCZNWV1ADKDL4J8E3JF5SW1UI2D9251SYDJIRYSRF1J4FK17HEYKOUU4XKS7HNMBZV7SANJZARN8F07S6NVLTE4NC5APHYH1', 'b62664dc66a5bcb1d6dec3c535606ff4:030000434308:42:2023-08-08::');
    '''

    # Execute the SQL commands
    try:
        cursor.execute(drop_tables_my)
    except:
        pass

    cursor.execute(create_table_fsm)
    cursor.execute(create_index_fsm)
    cursor.execute(create_table_barcodes)
    cursor.execute(create_index_barcodes)
    cursor.execute(create_table_balance)
    cursor.execute(create_index_balance)

    cursor.execute(insert_balance_1)
    cursor.execute(insert_balance_2)
    cursor.execute(insert_balance_3)
    cursor.execute(insert_balance_4)

    cursor.execute(insert_exit_barcodes_1)
    cursor.execute(insert_exit_barcodes_2)
    cursor.execute(insert_exit_barcodes_3)
    cursor.execute(insert_exit_barcodes_4)

    # Commit the transaction
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    print("Tables created successfully!")
