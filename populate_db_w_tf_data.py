import psycopg2
from tqdm import tqdm

# Database Connection Setup
def get_db_connection():
    return psycopg2.connect(
        dbname="AlgoMinds",
        user="algominds",
        password="machinedatabase",
        host="localhost",
        port=5432
    )

# Load SQL Query from the respective file
def load_query_template(interval):
    path = f'queries/{interval}_query_t.sql'
    with open(path, 'r') as file:
        return file.read()

# Execute Query for Given Date and Interval
def execute_batch_for_date(conn, date, interval):
    cur = conn.cursor()
    query_template = load_query_template(interval)
    final_query = query_template.replace('{{DATE}}', date)
    cur.execute(final_query)
    conn.commit()
    cur.close()

# Main Driver Function
def main():
    dates = [
        '2025-01-30', '2025-01-31', '2025-03-10', '2025-03-11', '2025-03-12',
        '2025-03-13', '2025-03-14', '2025-03-19', '2025-03-20', '2025-03-21',
        '2025-03-24', '2025-03-25', '2025-03-27', '2025-04-09', '2025-04-14',
        '2025-04-24', '2025-04-25', '2025-05-06', '2025-05-07', '2025-05-08',
        '2025-05-09', '2025-05-12', '2025-06-10', '2025-06-11', '2025-06-12',
        '2025-06-13', '2025-06-16', '2025-06-17', '2025-06-18', '2025-06-19',
        '2025-06-20', '2025-06-23', '2025-06-24', '2025-06-25', '2025-07-10',
        '2025-07-11', '2025-07-14', '2025-07-15', '2025-07-16', '2025-07-17',
        '2025-07-18', '2025-07-21', '2025-07-22'
    ]

    intervals = ['15min', '30min', '1h', '1d']

    conn = get_db_connection()
    total_tasks = len(dates) * len(intervals)

    with tqdm(total=total_tasks, desc="Factoring OHLCV Data", unit="task") as pbar:
        for date in dates:
            for interval in intervals:
                print(f"Processing {interval} for {date}...")
                execute_batch_for_date(conn, date, interval)
                pbar.update(1)

    conn.close()

if __name__ == "__main__":
    main()




# import psycopg2
# from psycopg2 import sql
# from tqdm import tqdm
# import time

# # PostgreSQL Connection Config
# DB_CONFIG = {
#     'host': 'localhost',
#     'dbname': 'AlgoMinds',
#     'user': 'algominds',
#     'password': 'machinedatabase',  # <- Change This
#     'port': 5432
# }

# # Dates to Process
# DATES = [
#     '2025-01-30', '2025-01-31', '2025-03-10', '2025-03-11', '2025-03-12', '2025-03-13', '2025-03-14',
#     '2025-03-19', '2025-03-20', '2025-03-21', '2025-03-24', '2025-03-25', '2025-03-27',
#     '2025-04-09', '2025-04-14', '2025-04-24', '2025-04-25',
#     '2025-05-06', '2025-05-07', '2025-05-08', '2025-05-09', '2025-05-12',
#     '2025-06-10', '2025-06-11', '2025-06-12', '2025-06-13', '2025-06-16', '2025-06-17', '2025-06-18', '2025-06-19', '2025-06-20', '2025-06-23', '2025-06-24', '2025-06-25',
#     '2025-07-10', '2025-07-11', '2025-07-14', '2025-07-15', '2025-07-16', '2025-07-17', '2025-07-18', '2025-07-21', '2025-07-22'
# ]

# # Symbols List
# SYMBOLS = ["786", "AABS", "AAL", "AASM", "AATM", "ABL", "ABOT", "ABSON", "ACIETF", "ACPL", "ADAMS", "ADMM", "ADOS", "ADTM", "AEL", "AGHA", "AGIC", "AGIL", "AGL", "AGLNCPS", "AGP", "AGSML", "AGTL", "AHCL", "AHL", "AHTM", "AICL", "AIRLINK", "AKBL", "AKDCL", "AKDHL", "AKDSL", "AKGL", "AKZO", "ALAC", "ALIFE", "ALNRS", "ALQT", "ALTN", "AMBL", "AMSL", "AMTEX", "ANL", "ANLPS", "ANNT", "ANSM", "ANTM", "APL", "APOT", "AQTM", "ARCTM", "ARM", "ARPAK", "ARPL", "ARUJ", "ASC", "ASCR1", "ASHT", "ASIC", "ASL", "ASLCPS", "ASLPS", "ASRL", "ASTL", "ASTM", "ATBA", "ATIL", "ATLH", "ATRL", "AVN", "AWTX", "AWWAL", "AYTM", "AYZT", "AZMT", "AZTM", "BAFL", "BAFS", "BAHL", "BAPL", "BATA", "BBFL", "BCL", "BCML", "BECO", "BEEM", "BELA", "BERG", "BFBIO", "BFMOD", "BGL", "BHAT", "BIFO", "BIIC", "BILF", "BIPL", "BIPLS", "BML", "BNL", "BNWM", "BOK", "BOP", "BPBL", "BPL", "BROT", "BRR", "BRRG", "BTL", "BUXL", "BWCL", "BWHL", "BYCO", "CASH", "CCM", "CECL", "CENI", "CEPB", "CFL", "CHAS", "CHBL", "CHCC", "CJPL", "CLCPS", "CLOUD", "CLOV", "CLVL", "CNERGY", "COLG", "COST", "CPAL", "CPHL", "CPPL", "CRTM", "CSAP", "CSIL", "CSM", "CTM", "CWSM", "CYAN", "DAAG", "DADX", "DATM", "DAWH", "DBCI", "DBSL", "DCL", "DCM", "DCR", "DCTL", "DEL", "DFML", "DFSM", "DGKC", "DIIL", "DINT", "DKL", "DKTM", "DLL", "DMIL", "DMTM", "DMTX", "DNCC", "DOL", "DOLCPS", "DOMF", "DSFL", "DSIL", "DSL", "DSML", "DWAE", "DWSM", "DWTM", "DYNO", "ECOP", "EFERT", "EFGH", "EFOODS", "EFUG", "EFUL", "ELCM", "ELSM", "EMCO", "ENGL", "ENGRO", "EPCL", "EPCLPS", "EPQL", "ESBL", "EWIC", "EWICR1", "EWLA", "EXIDE", "EXTR", "FABL", "FAEL", "FANM", "FASM", "FATIMA", "FCCL", "FCEL", "FCEPL", "FCIBL", "FCL", "FCONM", "FCSC", "FDIBL", "FDMF", "FDPL", "FECM", "FECTC", "FEM", "FEROZ", "FFBL", "FFC", "FFL", "FFLM", "FFLR1", "FHAM", "FIBLM", "FIL", "FIM", "FIMM", "FLYNG", "FLYNGR1", "FML", "FNBM", "FNEL", "FPJM", "FPRM", "FRCL", "FRSM", "FSWL", "FTHM", "FTMM", "FTSM", "FUDLM", "FZCM", "GADT", "GAIL", "GAL", "GAMON", "GASF", "GATI", "GATM", "GCIL", "GCILB", "GEMBCEM", "GEMBLUEX", "GEMMEL", "GEMPAPL", "GEMSPNL", "GEMUNSL", "GENP", "GFIL", "GGGL", "GGGLR1", "GGL", "GGLR1", "GHGL", "GHNI", "GHNL", "GIL", "GLAT", "GLAXO", "GLOT", "GLPL", "GOC", "GOEM", "GRR", "GRYL", "GSKCH", "GSPM", "GTECH", "GTECHBR", "GTYR", "GUSM", "GUTM", "GVGL", "GWLC", "HABSM", "HACC", "HADC", "HAEL", "HAFL", "HAJT", "HAL", "HALEON", "HASCOL", "HASCOLR1", "HATM", "HBL", "HBLTETF", "HCAR", "HCL", "HGFA", "HICL", "HIFA", "HINO", "HINOON", "HIRAT", "HKKT", "HMB", "HMICL", "HMIM", "HMM", "HPL", "HRPL", "HSM", "HSMCPS", "HSMPSR", "HSPI", "HTL", "HUBC", "HUMNL", "HUSI", "HWQS", "IBFL", "IBLHL", "ICCI", "ICCT", "ICI", "ICIBL", "ICL", "IDRT", "IDSM", "IDYM", "IFSL", "IGIBL", "IGIHL", "IGIIL", "IGIL", "ILP", "ILTM", "IMAGE", "IMAGER1", "IML", "IMS", "IMSL", "INDU", "INIL", "INKL", "INMF", "IPAK", "ISHT", "ISIL", "ISL", "ISTM", "ITSL", "ITTEFAQ", "JATM", "JDMT", "JDWS", "JGICL", "JKSM", "JLICL", "JOPP", "JOVC", "JPGL", "JSBL", "JSBLR1", "JSCL", "JSCLPSA", "JSCLR1", "JSGBETF", "JSGCL", "JSIL", "JSMFETF", "JSML", "JUBS", "JVDC", "JVDCPS", "KACM", "KAKL", "KAPCO", "KASBM", "KCL", "KEL", "KHSM", "KHTC", "KHYT", "KML", "KOHC", "KOHE", "KOHP", "KOHTM", "KOIL", "KOSM", "KPUS", "KSBP", "KSTM", "KTML", "LCI", "LEUL", "LINDE", "LIVEN", "LMSM", "LOADS", "LOTCHEM", "LPCL", "LPGL", "LPL", "LSECL", "LSEFSL", "LSEPL", "LSEVL", "LUCK", "MACFL", "MACTER", "MARI", "MCB", "MCBAH", "MCBIM", "MDTL", "MDTM", "MEBL", "MEHT", "MERIT", "META", "MFFL", "MFL", "MFTM", "MIIETF", "MIRKS", "MLCF", "MLCFR1", "MODAM", "MODAMR1", "MOHE", "MOIL", "MOON", "MQTM", "MRNS", "MSCL", "MSOT", "MSOTPS", "MTIL", "MTL", "MUBT", "MUGHAL", "MUGHALR1", "MUKT", "MUREB", "MWMP", "MZNPETF", "MZSM", "NAFL", "NAGC", "NATF", "NATM", "NBP", "NBPGETF", "NCL", "NCML", "NCPL", "NESTLE", "NETSOL", "NEXT", "NIB", "NICL", "NINA", "NITGETF", "NMFL", "NML", "NONS", "NORS", "NPL", "NPSM", "NRL", "NRSL", "NSRM", "OBOY", "OBOYR1", "OCTOPUS", "OGDC", "OLPL", "OLPM", "OLSM", "OML", "ORIXM", "ORM", "OTSU", "PABC", "PACE", "PAEL", "PAKCEM", "PAKD", "PAKL", "PAKMI", "PAKOXY", "PAKRI", "PAKT", "PASL", "PASM", "PCAL", "PCML", "PDGH", "PECO", "PELPS", "PGCL", "PGF", "PGIC", "PGLC", "PHDL", "PIAA", "PIAB", "PIAHCLA", "PIAHCLB", "PIBTL", "PICL", "PICT", "PIF", "PIL", "PIM", "PINL", "PIOC", "PKGI", "PKGP", "PKGS", "PMI", "PMPK", "PMRS", "PNGRS", "PNSC", "POL", "POML", "POWER", "POWERPS", "POWERR1", "PPL", "PPP", "PPVC", "PREMA", "PRET", "PRIB", "PRIC", "PRL", "PRLR1", "PRWM", "PSEL", "PSMC", "PSO", "PSX", "PSYL", "PTC", "PTL", "PUDF", "QUET", "QUICE", "QUSW", "RAVT", "RCML", "REDCO", "REGAL", "REWM", "RICL", "RMPL", "RPL", "RUBY", "RUPL", "SAIF", "SALT", "SANE", "SANSM", "SAPL", "SAPT", "SARC", "SASML", "SAZEW", "SBL", "SCBPL", "SCHT", "SCL", "SDIL", "SDOT", "SEARL", "SEARLR1", "SEL", "SEPCO", "SEPL", "SERF", "SERT", "SFAT", "SFL", "SFLL", "SGABL", "SGF", "SGFL", "SGPL", "SHCI", "SHCM", "SHDT", "SHEL", "SHEZ", "SHFA", "SHJS", "SHNI", "SHSML", "SIBL", "SICL", "SIEM", "SILK", "SINDM", "SING", "SITC", "SJTM", "SKRS", "SLCL", "SLCPA", "SLGL", "SLL", "SLSO", "SLYT", "SMBL", "SMBLCPSA", "SMBLCPSB", "SMCPL", "SML", "SMTM", "SNAI", "SNBL", "SNGP", "SPEL", "SPL", "SPLC", "SPWL", "SRSM", "SRVI", "SSGC", "SSIC", "SSML", "SSOM", "STCL", "STJT", "STML", "STPL", "STYLERS", "SUCM", "SUHJ", "SURAJ", "SURC", "SUTM", "SYM", "SYS", "SZTM", "TAJT", "TATM", "TBL", "TCLTC", "TCORP", "TCORPCPS", "TCORPR1", "TDIL", "TELE", "TGL", "THALL", "THAS", "THCCL", "TICL", "TOMCL", "TOWL", "TPL", "TPLI", "TPLL", "TPLP", "TPLRF1", "TPLT", "TREET", "TREI", "TRG", "TRIBL", "TRIPF", "TRPOL", "TRSM", "TSBL", "TSMF", "TSML", "TSPL", "UBDL", "UBL", "UBLPETF", "UCAPM", "UDLI", "UDPL", "UNIC", "UNITY", "UNITYR1", "UPFL", "USMT", "UVIC", "WAHN", "WAVES", "WAVESAPP", "WAVESR1", "WHALE", "WTL", "WYETH", "YOUW", "ZAHID", "ZELP", "ZHCM", "ZIL", "ZTL"]  # <-- Add your symbols here

# # Load the Query Templates (interval queries with placeholders {date} and {symbol})
# def load_query(file_path):
#     with open(file_path, 'r') as f:
#         return f.read()

# QUERY_FILES = {
#     '15m': 'queries/15min_query_t.sql',
#     '30m': 'queries/30min_query_t.sql',
#     '1h': 'queries/1h_query_t.sql',
#     '1d': 'queries/1d_query_t.sql'
# }

# queries = {k: load_query(v) for k, v in QUERY_FILES.items()}

# # Database Execution
# def execute_query(conn, query, trading_day, symbol):
#     with conn.cursor() as cur:
#         final_query = query.replace('{{DATE}}', trading_day).replace('{{SYMBOL}}', symbol)
#         print(f"Executing for {symbol} on {trading_day}...")
#         cur.execute(final_query)
#     conn.commit()

# # Main Execution Loop
# def main():
#     total_tasks = len(DATES) * len(SYMBOLS) * len(queries)
#     conn = psycopg2.connect(**DB_CONFIG)
#     try:
#         with tqdm(total=total_tasks, desc="Factoring OHLCV Data", unit="task", dynamic_ncols=True) as pbar:
#             for date in DATES:
#                 for symbol in SYMBOLS:
#                     for interval, query in queries.items():
#                         execute_query(conn, query, date, symbol)
#                         pbar.set_postfix(symbol=symbol, date=date, interval=interval)
#                         pbar.update(1)
#         print("✅ All OHLCV data factored successfully.")
#     finally:
#         conn.close()
        
# if __name__ == '__main__':
#     main()
