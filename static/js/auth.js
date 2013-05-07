var jsonAuthUrl = "../auth";

$(function() {
  $("#flickrAppInput").hide();
  $("#facebookAppInput").hide();
  $("#tumblrAppInput").hide();
  $("#twitterAppInput").hide();
  onAuthShow();  
});


function onAuthShow()
{
    $.ajax({
    url: jsonAuthUrl,
    dataType: 'json',
    async: false,
    data: {authStatus: 0},
    success: function(json) {
      
      if (json.flickr == false)
      {
        $("#flickrAppInput").show();
        $("#flickrStatus").addClass("authFalse");
        $("#flickrStatus").removeClass("authTrue");
      }
      else
      {
        $("#flickrStatus").removeClass("authFalse");
        $("#flickrStatus").addClass("authTrue");
      }
      
      if (json.facebook == false)
      {
        $("#facebookAppInput").show();
        $("#facebookStatus").addClass("authFalse");
        $("#facebookStatus").removeClass("authTrue");
      }
      else
      {
        $("#facebookStatus").removeClass("authFalse");
        $("#facebookStatus").addClass("authTrue");
      }
      
      if (json.tumblr == false)
      {
        $("#tumblrAppInput").show();
        $("#tumblrStatus").addClass("authFalse");
        $("#tumblrStatus").removeClass("authTrue");
      }
      else
      {
        $("#tumblrStatus").removeClass("authFalse");
        $("#tumblrStatus").addClass("authTrue");
      }

      if (json.twitter == false)
      {
        $("#twitterAppInput").show();
        $("#twitterStatus").addClass("authFalse");
        $("#twitterStatus").removeClass("authTrue");
      }
      else
      {
        $("#twitterStatus").removeClass("authFalse");
        $("#twitterStatus").addClass("authTrue");
      }
    }
  });
}

$("#flickrAppInputSubmit").click(function () {
  var apiKey = $("#flickrAPIKey").val();
  var apiSecret= $("#flickrAPISecret").val();

  submitDict = { "submitInitial":0, "apiKey":apiKey, "apiSecret":apiSecret }
  
  $.ajax({
    type: 'POST',
    url: "../auth/flickrAuth",
    dataType: 'json',
    async: false,
    data: submitDict,
    success: function(json) {
      window.location.replace(json.redirectURL);
    },
    error: function(XMLHttpRequest, textStatus, errorThrown) {
      alert("Flickr auth failed - check your key/secret values");
    }
  });
});


$("#facebookAppInputSubmit").click(function () {
  var apiKey = $("#facebookAPIKey").val();
  var apiSecret= $("#facebookAPISecret").val();

  submitDict = { "submitInitial":0, "apiKey":apiKey, "apiSecret":apiSecret }
  
  $.ajax({
    type: 'POST',
    url: "../auth/facebookAuth",
    dataType: 'json',
    async: false,
    data: submitDict,
    success: function(json) {
      window.location.replace(json.redirectURL);
    },
    error: function(XMLHttpRequest, textStatus, errorThrown) {
      alert("Facebook auth failed - check your key/secret values");
    }
  });
});


$("#tumblrAppInputSubmit").click(function () {
  var apiKey = $("#tumblrAPIKey").val();
  var apiSecret= $("#tumblrAPISecret").val();
  var blogURL = $("#tumblrBlogURL").val();
  
  submitDict = { "submitInitial":0, "apiKey":apiKey, "apiSecret":apiSecret, "blogURL":blogURL }
  
  $.ajax({
    type: 'POST',
    url: "../auth/tumblrAuth",
    dataType: 'json',
    async: false,
    data: submitDict,
    success: function(json) {
      window.location.replace(json.redirectURL);
    },
    error: function(XMLHttpRequest, textStatus, errorThrown) {
      alert("Tumblr auth failed - check your key/secret values");
    }
  });
});


$("#twitterAppInputSubmit").click(function () {
  var apiKey = $("#twitterAPIKey").val();
  var apiSecret= $("#twitterAPISecret").val();

  submitDict = { "submitInitial":0, "apiKey":apiKey, "apiSecret":apiSecret }
  
  $.ajax({
    type: 'POST',
    url: "../auth/twitterAuth",
    dataType: 'json',
    async: false,
    data: submitDict,
    success: function(json) {
      window.location.replace(json.redirectURL);
    },
    error: function(XMLHttpRequest, textStatus, errorThrown) {
      alert("Twitter auth failed - check your key/secret values");
    }
  });
});