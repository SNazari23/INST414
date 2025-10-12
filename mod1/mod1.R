##Gym 
gym_df <- subset(spotify_sports_playlists, sport == "gym")
gym_df <- aggregate(
  list(count = rep(1, nrow(gym_df))),
  by = list(song = gym_df$song, artist = gym_df$artist, album = gym_df$album),
  FUN = sum
)

gym_df <- gym_df[order(-gym_df$count), ]
head(gym_df, 10)

##Golf
golf_df <- subset(spotify_sports_playlists, sport == "golf")
golf_df <- aggregate(
  list(count = rep(1, nrow(golf_df))),
  by = list(song = golf_df$song, artist = golf_df$artist, album = golf_df$album),
  FUN = sum
)
golf_df <- golf_df[order(-golf_df$count), ]
head(golf_df, 10)

##Tennis
tennis_df <- subset(spotify_sports_playlists, sport == "tennis")
tennis_df <- aggregate(
  list(count = rep(1, nrow(tennis_df))),
  by = list(song = tennis_df$song, artist = tennis_df$artist, album = tennis_df$album),
  FUN = sum
)
tennis_df <- tennis_df[order(-tennis_df$count), ]
head(tennis_df, 10)

##basketball
basketball_df <- subset(spotify_sports_playlists, sport == "basketball")
basketball_df <- aggregate(
  list(count = rep(1, nrow(basketball_df))),
  by = list(song = basketball_df$song, artist = basketball_df$artist, album = basketball_df$album),
  FUN = sum
)
basketball_df <- basketball_df[order(-basketball_df$count), ]
head(basketball_df, 10)

##soccer
soccer_df <- subset(spotify_sports_playlists, sport == "soccer")
soccer_df <- aggregate(
  list(count = rep(1, nrow(soccer_df))),
  by = list(song = soccer_df$song, artist = soccer_df$artist, album = soccer_df$album),
  FUN = sum
)
soccer_df <- soccer_df[order(-soccer_df$count), ]
head(soccer_df, 10)

##football
football_df <- subset(spotify_sports_playlists, sport == "football")
football_df <- aggregate(
  list(count = rep(1, nrow(football_df))),
  by = list(song = football_df$song, artist = football_df$artist, album = football_df$album),
  FUN = sum
)
football_df <- football_df[order(-football_df$count), ]
head(football_df, 10)

##running
run_df <- subset(spotify_sports_playlists, sport == "running")
run_df <- aggregate(
  list(count = rep(1, nrow(run_df))),
  by = list(song = run_df$song, artist = run_df$artist, album = run_df$album),
  FUN = sum
)
run_df <- run_df[order(-run_df$count), ]
head(run_df, 10)

##all active 
active_df <- aggregate(
  list(count = rep(1, nrow(spotify_sports_playlists))),
  by = list(
    song = spotify_sports_playlists$song, 
    artist = spotify_sports_playlists$artist, 
    album = spotify_sports_playlists$album
  ),
  FUN = sum
)

active_df <- active_df[order(-active_df$count), ]
head(active_df, 10)
