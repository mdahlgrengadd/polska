import sys ,os, argparse, requests, urllib, re
from urllib.parse import unquote
from urllib.parse import quote
import ctypes
from unidecode import unidecode

def main():
    welcome_message = '''
    ####################################
    #       FolkRNN ABC parser         #
    # Downloads songs from folkwiki.se #
    #     and saves to a folder        #
    #        Use on the url:           #
    # http://www.folkwiki.se/pub/cache #
    ####################################
    '''
    parser = argparse.ArgumentParser(description=welcome_message)
    parser.add_argument("-u", "--url", help="the url with listing of all songs")
    parser.add_argument("-f", "--filter", help="must be in the filename of the song")
    parser.add_argument("-d", "--download_path", help="folder for downloads")
    args = parser.parse_args()

    print("Checking %s for songs..." % args.url)
    songs_to_download = get_song_list(args.url, args.filter)
    print("Found %d songs at %s" % (len(songs_to_download), args.url))
    if not os.path.isdir('./%s' % args.download_path):
        create_dir = input("Could not find directory %s, create it? [Y/n]" % args.download_path)
        if create_dir == 'y' or create_dir == 'Y':
            os.makedirs('./%s' % args.download_path)
        else:
            print("Aborting bc no download directory")
            quit()
    print("Starting download to: %s" % args.download_path)
    download_all_songs(songs_to_download, args.download_path)


def download_all_songs_old(song_list, download_dir):
    count = 1
    for song in song_list:
        print('\rDownloading song %d/%d...' % (count, len(song_list)), end="")
        song_without_url = song.split("/")[-1]
        decoded_song = urllib.parse.unquote(song_without_url)  # Decode the URL-encoded filename
        decoded_song = decoded_song.encode('iso-8859-1').decode('utf-8')  # From ISO-8859-1 to UTF-8
        file_path = os.path.join(download_dir, decoded_song)
        urllib.request.urlretrieve(song, file_path)
        count += 1
    print('\rDownload complete                    ')

def download_all_songs(song_list, download_dir):
    count = 1
    for song in song_list:
        print('\rDownloading song %d/%d...' % (count, len(song_list)), end="")
        try:
            response = requests.get(song, stream=True)
            try:
                content = response.content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    content = response.content.decode('ISO-8859-1')
                except UnicodeDecodeError:
                    print(f"Could not decode song {count}")
                    continue
            
            title_line = next((line for line in content.split('\n') if line.startswith('T:')), None)
            if title_line is None:
                print(f"No title found for song {count}")
                continue

            title = title_line[2:].strip().replace('/', '_').replace('\\', '_')
            
            # Check if title is a 32 character hexadecimal hash
            if len(title) == 32 and all(c in "0123456789abcdef" for c in title.lower()):
                print(f"Title for song {count} is a hexadecimal hash, skipping download.")
                continue

            file_path = os.path.join(download_dir, title + '.abc')

            fd = os.open(file_path, os.O_WRONLY | os.O_CREAT)
            with open(fd, 'w') as f:
                f.write(content)

        except Exception as e:
            print(f"\nError while processing song {count}: {str(e)}")
        finally:
            count += 1
    print('\rDownload complete                    ')


def get_song_list(url, song_filter):
    #Fetch source
    response = requests.get(url)
    data = response.text
    data = data.split('\n')
    #filter out all lines with links in them
    links = [ x for x in data if 'href' in x and song_filter in x ]
    #Replace the . in filter for regex safe \.
    regex = re.compile(r"a href=\"(.*%s)\"" % "\.".join(song_filter.split(".")))
    all_filtered_links = []
    for link in links:
        match = regex.search(link)
        all_filtered_links.append(match.group(1))
    #There might be doubles, that only have a different affix (<song>_efbd9.latin.abc)
    only_uniques = {}
    for link in all_filtered_links:
        #link = unquote(link)
        split_on_filename = link.split(".")
        split_on_underscore = split_on_filename[0].split("_")
        #some filenames are just gibbereish, they dont split on _
        if len(split_on_underscore) == 1:
            only_uniques[split_on_filename[0]] = "%s/%s" % (url, link)
            continue
        #everything besides the unique identifier
        song_name = '_'.join(split_on_underscore[:-1])
        
        #The list is ordered, so we just replace it if its
        #already there
        only_uniques[song_name] = "%s/%s" % (url, link)
    #All done!
    return only_uniques.values()

if __name__ == '__main__':
    main()
