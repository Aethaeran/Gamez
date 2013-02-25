import ConfigParser
import os
import base64
import hashlib
import random
import gamez

def CheckConfigForAllKeys():
    changesMade = False
    config = ConfigParser.RawConfigParser()
    configfile = os.path.abspath(gamez.CONFIG_PATH)
    config.read(configfile)

    if(config.has_section('global') == False):
        config.add_section('global')
        changesMade = True

    if(config.has_section('nzbsrus') == False):
        config.add_section('nzbsrus')
        changesMade = True

    if(config.has_section('Sabnzbd') == False):
        config.add_section('Sabnzbd')
        changesMade = True

    if(config.has_section('Blackhole') == False):
        config.add_section('Blackhole')
        changesMade = True

    if(config.has_section('Scheduler') == False):
        config.add_section('Scheduler')
        changesMade = True

    if(config.has_section('NZBSU') == False):
        config.add_section('NZBSU')
        changesMade = True

    if(config.has_section('SystemGenerated') == False):
        config.add_section('SystemGenerated')
        changesMade = True

    if(config.has_section('Newznab') == False):
        config.add_section('Newznab')
        changesMade = True
     
    if(config.has_section('Notifications') == False):
        config.add_section('Notifications')
        changesMade = True

    if(config.has_section('Folders') == False):
        config.add_section('Folders')
        changesMade = True
    
    if(config.has_option('global','server.socket_host') == False):
        config.set('global','server.socket_host','"0.0.0.0"')
        changesMade = True

    if(config.has_option('global','gamez_port') == False):
        config.set('global','gamez_port','8085')
        changesMade = True

    if(config.has_option('global','user_name') == False):
        config.set('global','user_name','""')
        changesMade = True
        
    if(config.has_option('global','password') == False):
        config.set('global','password','""')
        changesMade = True

    if(config.has_option('global','debug_enabled') == False):
        config.set('global','debug_enabled','')
        changesMade = True        

    if(config.has_option('nzbsrus','username') == False):
        config.set('nzbsrus','username','""')
        changesMade = True

    if(config.has_option('nzbsrus','api_key') == False):
        config.set('nzbsrus','api_key','""')
        changesMade = True

    if(config.has_option('Sabnzbd','api_key') == False):
        config.set('Sabnzbd','api_key','""')
        changesMade = True

    if(config.has_option('Sabnzbd','host') == False):
        config.set('Sabnzbd','host','"127.0.0.1"')
        changesMade = True

    if(config.has_option('Sabnzbd','port') == False):
        config.set('Sabnzbd','port','')
        changesMade = True

    if(config.has_option('Sabnzbd','category') == False):
        config.set('Sabnzbd','category','')
        changesMade = True

    if(config.has_option('Sabnzbd','folder') == False):
        config.set('Sabnzbd','folder','')
        changesMade = True

    if(config.has_option('Scheduler','download_interval') == False):
        config.set('Scheduler','download_interval','60')
        changesMade = True
        
    if(config.has_option('Scheduler','game_list_update_interval') == False):
        config.set('Scheduler','game_list_update_interval','1440')
        changesMade = True

    if(config.has_option('SystemGenerated','is_to_ignore_update') == False):
        config.set('SystemGenerated','is_to_ignore_update','0')
        changesMade = True

    if(config.has_option('SystemGenerated','ignored_version') == False):
        config.set('SystemGenerated','ignored_version','""')
        changesMade = True

    if(config.has_option('SystemGenerated','sabnzbd_enabled') == False):
        config.set('SystemGenerated','sabnzbd_enabled','0')
        changesMade = True
        
    if(config.has_option('SystemGenerated','nzbsrus_enabled') == False):
        config.set('SystemGenerated','nzbsrus_enabled','0')
        changesMade = True
        
    if(config.has_option('SystemGenerated','nzbsu_enabled') == False):
        config.set('SystemGenerated','nzbsu_enabled','0')
        changesMade = True
  
    if(config.has_option('SystemGenerated','newznab_enabled') == False):
        config.set('SystemGenerated','newznab_enabled','0')
        changesMade = True        

    if(config.has_option('SystemGenerated','prowl_enabled') == False):
        config.set('SystemGenerated','prowl_enabled','0')
        changesMade = True   
        
    if(config.has_option('SystemGenerated','growl_enabled') == False):
        config.set('SystemGenerated','growl_enabled','0')
        changesMade = True   
        
    if(config.has_option('SystemGenerated','notifo_enabled') == False):
        config.set('SystemGenerated','notifo_enabled','0')
        changesMade = True   
        
    if(config.has_option('SystemGenerated','notifymyandroid_enabled') == False):
        config.set('SystemGenerated','notifymyandroid_enabled','0')
        changesMade = True 

    if(config.has_option('SystemGenerated','xbmc_enabled') == False):
        config.set('SystemGenerated','xbmc_enabled','0')
        changesMade = True

    if(config.has_option('SystemGenerated','blackhole_nzb_enabled') == False):
        config.set('SystemGenerated','blackhole_nzb_enabled','0')
        changesMade = True  
        
    if(config.has_option('SystemGenerated','blackhole_torrent_enabled') == False):
        config.set('SystemGenerated','blackhole_torrent_enabled','0')
        changesMade = True         

    if(config.has_option('SystemGenerated','torrent_kat_enabled') == False):
        config.set('SystemGenerated','torrent_kat_enabled','0')
        changesMade = True  
        
    if(config.has_option('SystemGenerated','process_torrent_download_folder_enabled') == False):
        config.set('SystemGenerated','process_torrent_download_folder_enabled','0')
        changesMade = True     
        
    if(config.has_option('SystemGenerated','process_nzb_download_folder_enabled') == False):
        config.set('SystemGenerated','process_nzb_download_folder_enabled','0')
        changesMade = True          
        
    if(config.has_option('SystemGenerated','process_sabnzbd_download_folder_enabled') == False):
        config.set('SystemGenerated','process_sabnzbd_download_folder_enabled','0')
        changesMade = True     
        
    if(config.has_option('SystemGenerated','process_download_folder_wii_enabled') == False):
        config.set('SystemGenerated','process_download_folder_wii_enabled','0')
        changesMade = True   
        
    if(config.has_option('SystemGenerated','process_download_folder_ps3_enabled') == False):
        config.set('SystemGenerated','process_download_folder_ps3_enabled','0')
        changesMade = True         
    
    if(config.has_option('SystemGenerated','process_download_folder_pc_enabled') == False):
        config.set('SystemGenerated','process_download_folder_pc_enabled','0')
        changesMade = True    

    if(config.has_option('SystemGenerated','process_download_folder_xbox360_enabled') == False):
        config.set('SystemGenerated','process_download_folder_xbox360_enabled','0')
        changesMade = True    
 		
    if(config.has_option('SystemGenerated','default_search') == False):
        config.set('SystemGenerated','default_search','"---"')
        changesMade = True  
    
    if(config.has_option('SystemGenerated','ps3_tb_enable') == False):
        config.set('SystemGenerated','ps3_tb_enable','0')
        changesMade = True
    
    if(config.has_option('SystemGenerated','ps3_jb_enable') == False):
        config.set('SystemGenerated','ps3_jb_enable','0')
        changesMade = True
    
    if(config.has_option('SystemGenerated','blacklist_words_xbox360') == False):
        config.set('SystemGenerated','blacklist_words_xbox360','""')
        changesMade = True
     
    if(config.has_option('SystemGenerated','blacklist_words_wii') == False):
        config.set('SystemGenerated','blacklist_words_wii','""')
        changesMade = True 

    if(config.has_option('SystemGenerated','api_key') == False):
        apiKey = base64.b64encode(hashlib.sha256( str(random.getrandbits(256)) ).digest(), random.choice(['rA','aZ','gQ','hH','hG','aR','DD'])).rstrip('==')
        config.set('SystemGenerated','api_key','"' + apiKey + '"')
        changesMade = True

    if(config.has_option('SystemGenerated','webinterface') == False):
        config.set('SystemGenerated','webinterface','"default"')
        changesMade = True
 
    if(config.has_option('SystemGenerated','clearlog_at_startup') == False):
        config.set('SystemGenerated','clearlog_at_startup','1')
        changesMade = True

    if(config.has_option('SystemGenerated','https_support_enabled') == False):
        config.set('SystemGenerated','https_support_enabled','0')
        changesMade = True

    if(config.has_option('SystemGenerated','retention') == False):
        config.set('SystemGenerated','retention','1100')
        changesMade = True

    if(config.has_option('Newznab','api_key') == False):
        config.set('Newznab','api_key','""')
        changesMade = True

    if(config.has_option('Newznab','wii_category_id') == False):
        config.set('Newznab','wii_category_id','"1030"')
        changesMade = True

    if(config.has_option('Newznab','xbox360_category_id') == False):
        config.set('Newznab','xbox360_category_id','"1050"')
        changesMade = True

    if(config.has_option('Newznab','ps3_category_id') == False):
        config.set('Newznab','ps3_category_id','"1060"')
        changesMade = True

    if(config.has_option('Newznab','pc_category_id') == False):
        config.set('Newznab','pc_category_id','"1070"')
        changesMade = True
	
    if(config.has_option('Newznab','host') == False):
        config.set('Newznab','host','""')
        changesMade = True

    if(config.has_option('Newznab','port') == False):
        config.set('Newznab','port','')
        changesMade = True

    if(config.has_option('Notifications','prowl_api') == False):
        config.set('Notifications','prowl_api','""')
        changesMade = True

    if(config.has_option('Notifications','growl_host') == False):
        config.set('Notifications','growl_host','""')
        changesMade = True

    if(config.has_option('Notifications','growl_port') == False):
        config.set('Notifications','growl_port','23053')
        changesMade = True

    if(config.has_option('Notifications','growl_password') == False):
        config.set('Notifications','growl_password','""')
        changesMade = True	

    if(config.has_option('Notifications','notifo_username') == False):
        config.set('Notifications','notifo_username','""')
        changesMade = True	

    if(config.has_option('Notifications','notifo_apikey') == False):
        config.set('Notifications','notifo_apikey','""')
        changesMade = True

    if(config.has_option('Notifications','notifymyandroid_apikey') == False):
        config.set('Notifications','notifymyandroid_apikey','""')
        changesMade = True

    if(config.has_option('Notifications','xbmc_username') == False):
        config.set('Notifications','xbmc_username','""')
        changesMade = True	

    if(config.has_option('Notifications','xbmc_password') == False):
        config.set('Notifications','xbmc_password','""')
        changesMade = True

    if(config.has_option('Notifications','xbmc_hosts') == False):
        config.set('Notifications','xbmc_hosts','""')
        changesMade = True

    if(config.has_option('Blackhole','nzb_blackhole_path') == False):
        config.set('Blackhole','nzb_blackhole_path','""')
        changesMade = True	

    if(config.has_option('Blackhole','torrent_blackhole_path') == False):
        config.set('Blackhole','torrent_blackhole_path','""')
        changesMade = True	

    if(config.has_option('Folders','torrent_completed') == False):
        config.set('Folders','torrent_completed','""')
        changesMade = True	

    if(config.has_option('Folders','nzb_completed') == False):
        config.set('Folders','nzb_completed','""')
        changesMade = True	

    if(config.has_option('Folders','wii_destination') == False):
        config.set('Folders','wii_destination','""')
        changesMade = True	

    if(config.has_option('Folders','xbox360_destination') == False):
        config.set('Folders','xbox360_destination','""')
        changesMade = True	

    if(config.has_option('Folders','ps3_destination') == False):
        config.set('Folders','ps3_destination','""')
        changesMade = True	

    if(config.has_option('Folders','pc_destination') == False):
        config.set('Folders','pc_destination','""')
        changesMade = True	
		
    if(config.has_option('NZBSU','api_key') == False):
        config.set('NZBSU','api_key','""')
        changesMade = True

    if(changesMade):
        with open(configfile,'wb') as configFile:
            config.write(configFile)
