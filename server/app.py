from flask import request, jsonify, make_response, session
from flask_restful import Resource
from models import Artist, Playlist, Song, User, PlaylistSong
from config import app, api, db

@app.route('/')
def index():
    return '<h1> Tuneverse </h1>'

class Login(Resource):
    def post(self):
        data = request.get_json()
        name = data.get('name')
        password = data.get('password')
        
        user = User.query.filter_by(name=name).first()
        if user and user.authenticate(password): 
            session['user_id'] = user.id 
            return {'user_id': user.id}, 200
        else:
            return {'message': 'Invalid username or password'}, 401
        


class Signup (Resource):
    def post ( self ):
        data = request.json
        username = data['name']
        password = data['password']

        user = User.query.filter_by(name=username).first()
        if user: 
            return make_response({'error': 'username taken be original'}, 404)

        new_user = User(username=username,password_hash=password)
        db.session.add(new_user)
        db.session.commit()
        session ['user_id'] = new_user.id
        return make_response({'message': 'user created successfully'}, 200)

class Logout (Resource):
    def delete (self):
        session['user_id'] = None
        return make_response ({'message': 'User logged out'},204)

class Authenticate (Resource):
    def get (self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user: 
            return make_response(user.to_dict(),200)
        else:
            return make_response({'error': 'no active user found in database'},401)
        

    ############ writing fetchs##

class Songs(Resource):
    def get(self):
        songs = Song.query.all()
        song_names= [song.to_dict(only = ('id', 'title')) for song in songs]
    
        return make_response (song_names, 200 )
    
    
class SongsByID (Resource):
    def get(self, id):
        song = Song.query.get(id)
        if not song:
            return make_response({'message': 'not found'}, 404 )
        return make_response (song.to_dict(only = ('id', 'title')), 200 )

class Artists(Resource):
    def get(self):
        artists = Artist.query.all()
        artist_names= [artist.to_dict(only = ("id","name", "image")) for artist in artists]        
        return make_response (artist_names, 200 )
    
class ArtistsByID (Resource):
    def get(self, id):
        artist = Artist.query.get(id)
        if not artist:
            return make_response({'message': 'not found'}, 404 )
        return make_response (artist.to_dict(), 200 )
    
class Playlists(Resource):
    def get(self):
        playlists = [p.to_dict(only = ("id","name","songs.id", "songs.title","artists")) for p in Playlist.query.all()]
        
        return make_response (playlists, 200)
    
    def post (self):
        data = request.get_json()
        name = data.get('name')
        if len(name) < 5:
            return ("Playlist name must be at least 5 characters.")

        try:
            newPlaylist = Playlist(name = data['name'])
        except ValueError as e : 
            return make_response({'error' : [str(e)]}, 422)
        
        db.session.add(newPlaylist)
        db.session.commit()
        return make_response (newPlaylist.to_dict(),201)
    


        
class PlaylistByID (Resource):
    def get(self, id):
        playlist = Playlist.query.get(id)
        if not playlist:
            return make_response({'message': 'not found'}, 404 )
        return make_response (playlist.to_dict(), 200 )
    
    def delete (self, id):
        playlist = Playlist.query.get_or_404(id)
    
        db.session.delete(playlist)
        db.session.commit()
    
        return make_response({'message': 'Playlist deleted successfully'}, 204)
    
    def patch(self, id):
        playlist = Playlist.query.get_or_404(id)
        data = request.get_json()
        
        for attr in data:
            setattr(playlist, attr, data[attr])
            
        db.session.commit()
        
        playlist_dict = playlist.to_dict()

        return make_response (playlist_dict, 202)

class UpdatePlaylist(Resource):
    def post(self, playlist_name):
        playlist = Playlist.query.filter_by(name=playlist_name).all()

        if not playlist:
            return {'message': 'Playlist not found'}, 404

        data = request.get_json()

        if 'songs' in data:
            playlist.songs = data['songs']

        db.session.commit()
        return {'message': 'Playlist updated successfully'}, 200

class PlaylistSongs (Resource):
    def post (self):
        data = request.get_json()
        newPs = PlaylistSong(song_id = data['song_id'], playlist_id = data ['playlist_id'])    
        db.session.add(newPs)
        db.session.commit()
        return make_response (newPs.to_dict(),201)
    
class PlaylistWithSongs(Resource):
    def post (self):
        data = request.get_json()
        playlist = Playlist(name = data ['name'])
        db.session.add(playlist)
        db.session.commit()
        
        for song_title in data['songs']: 
            song = Song.query.filter_by(title = song_title['title']).first()
            
            if not song: 
                song = Song(title = song_title['title'])
                db.session.add(song)
                db.session.commit()
                
            ps = PlaylistSong (song_id = song.id, playlist_id = playlist.id)
            db.session.add(ps)
            db.session.commit()
        return make_response(playlist.to_dict(), 201)
    
    

api.add_resource(Login, '/login')
api.add_resource(Signup, '/signup')
api.add_resource(Authenticate,'/authenticate')
api.add_resource(Logout, '/logout')
api.add_resource(Songs, '/songs')
api.add_resource(SongsByID, '/songs/<int:id>')
api.add_resource(Artists, '/artists')
api.add_resource(ArtistsByID, '/artists/<int:id>')
api.add_resource(Playlists, '/playlists')
api.add_resource(PlaylistByID, '/playlists/<int:id>')
api.add_resource(UpdatePlaylist, '/playlists/<playlist_name>/update')
api.add_resource(PlaylistSongs, '/playlistsongs')
api.add_resource(PlaylistWithSongs, '/playlistwithsongs')



if __name__ == '__main__':
    app.run(port=5555, debug=True)

