#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    artist = db.relationship('Artist', backref=db.backref('shows', cascade='all, delete'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    venue = db.relationship('Venue', backref=db.backref('shows', cascade='all, delete'))
    start_time = db.Column(db.DateTime())


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(str(value))
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    unique_venue_locations = Venue.query.distinct(Venue.city, Venue.state).all()
    data = [
        {
            "city": loc.city,
            "state": loc.state,
            "venues": Venue.query.filter(Venue.city == loc.city and Venue.state == loc.state)
        } for loc in unique_venue_locations
    ]

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term')
    venues = Venue.query.filter(Venue.name.ilike("%{}%".format(search_term))).all()

    response = {
        "count": len(venues),
        "data": [v for v in venues]
    }
    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get('search_term', '')
    )


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    return render_template('pages/show_venue.html', venue=Venue.query.get(venue_id))

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    # body = {}
    try:
        result = VenueForm(request.form)
        venue = Venue(
            name=result.name.data,
            city=result.city.data,
            state=result.state.data,
            phone=result.phone.data,
            genres=result.genres.data,
            facebook_link=result.facebook_link.data,
            image_link=result.image_link.data
        )
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        # on failure db insert, flash error
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue_to_delete = Venue.query.filter(Venue.id == venue_id).one()
        venue_to_delete.delete()
        flash("Venue " + venue_to_delete[0]['name'] + " was successfully deleted!")
    except:
        flash("Venue " + venue_to_delete[0]['name'] + " could not be deleted")
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    return render_template(
        'pages/artists.html',
        artists=Artist.query.order_by('id').all()
    )


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term')
    artists = Artist.query.filter(Artist.name.ilike("%{}%".format(search_term))).all()

    response={
        "count": len(artists),
        "data": [a for a in artists]
    }
    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get('search_term', '')
    )


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    return render_template(
        'pages/show_artist.html',
        artist=Artist.query.get(artist_id)
    )

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    return render_template('forms/edit_artist.html', form=form, artist=Artist.query.get(artist_id))


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # artist record with ID <artist_id> using the new attributes
    try:
        result = ArtistForm(request.form)
        artist = Artist.query.get(artist_id)
        artist.name = result.name.data
        artist.genres = result.genres.data
        artist.city = result.city.data
        artist.state = result.state.data
        artist.phone = result.phone.data

        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    return render_template('forms/edit_venue.html', form=form, venue=Venue.query.get(venue_id))


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        result = VenueForm(request.form)
        venue = Venue.query.get(venue_id)
        venue.name = result.name.data
        venue.genres = result.genres.data
        venue.city = result.city.data
        venue.state = result.state.data
        venue.phone = result.phone.data

        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    error = False
    # body = {}
    try:
        result = ArtistForm(request.form)
        artist = Artist(
            name=result.name.data,
            city=result.city.data,
            state=result.state.data,
            phone=result.phone.data,
            genres=result.genres.data,
            facebook_link=result.facebook_link.data,
            image_link=result.image_link.data
        )
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        # on failure db insert, flash error
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    shows = Show.query.all()
    data = [{
        "venue_id": s.venue_id,
        "venue_name": Venue.query.filter(Venue.id == s.venue_id).all()[0].name,
        "artist_id": s.artist_id,
        "artist_name": Artist.query.filter(Artist.id == s.artist_id).all()[0].name,
        "artist_image_link": Artist.query.filter(Artist.id == s.artist_id).all()[0].image_link,
        "start_time": s.start_time
    } for s in shows]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    error = False
    try:
        result = ShowForm(request.form)
        show = Show(
            artist_id=result.artist_id.data,
            venue_id=result.venue_id.data,
            start_time=result.start_time.data
        )
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        # on failure db insert, flash error
        flash('An error occurred. Show could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Show was successfully listed!')

    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
