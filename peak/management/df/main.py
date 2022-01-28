import time

import config
from df import DF


if __name__ == '__main__':
    jid = config.df_jid
    df = DF(jid, jid)
    df.start().result()
    while df.is_alive():
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            df.stop()
    
