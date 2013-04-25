var jsonAuthUrl = "../auth";

$(function() {
  
  $.ajax({
    url: jsonAuthUrl,
    dataType: 'json',
    async: false,
    data: {authStatus: 0},
    success: function(json) {
      if (json.flickr == true)
      {
        $( "#flickrAuthStatus" ).text( "authorised" );
      }
      if (json.facebook == true)
      {
        $( "#facebookAuthStatus" ).text( "authorised" );
      }
      if (json.tumblr == true)
      {
        $( "#tumblrAuthStatus" ).text( "authorised" );
      }
      if (json.twitter == true)
      {
        $( "#twitterAuthStatus" ).text( "authorised" );
      }
    }
  });
});
