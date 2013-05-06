jQuery.ajaxSettings.traditional = true;

$(function() {
  $("#flickrSets").tagit();
  $("#flickrGroups").tagit();
  
  $("#latitude").filter_input({regex:'[0-9.]'}); 
  $("#longitude").filter_input({regex:'[0-9.]'}); 

  $("#latitude").button().addClass('styledInput');
  $("#longitude").button().addClass('styledInput');

  $("#addresspicker_map").button().addClass('styledInput');
  
  
  $("#templateList").selectable();

  setInterval( "slideSwitch()", 8000 );
});

function reverseDictLookup(dict, value)
{
  for (var key in dict)
  {
    if (dict[key] == value)
      return key;
  }
}

function showUploadImages()
{
  $("#uploadImages").show("drop");
  $("#imagesTab").hide("drop");
  $("#editBox").hide("drop");
  $("#authPage").hide("drop");
  $("#jobsPage").hide("drop");
}

function showAuth()
{
  $("#authPage").show("drop");
  $("#imagesTab").hide("drop");
  $("#editBox").hide("drop");
  $("#uploadImages").hide("drop");
  $("#jobsPage").hide("drop");
}

function showEditor()
{
  $("#editBox").show("drop");
  $("#imagesTab").hide("drop");
  $("#uploadImages").hide("drop");
  $("#authPage").hide("drop");
  $("#jobsPage").hide("drop");
}

function showMain()
{
  $("#imagesTab").show("drop");
  $("#editBox").hide("drop");
  $("#uploadImages").hide("drop");
  $("#authPage").hide("drop");
  $("#jobsPage").hide("drop");
}

function showJobs()
{
  $("#jobsPage").show("drop");
  $("#imagesTab").hide("drop");
  $("#editBox").hide("drop");
  $("#uploadImages").hide("drop");
  $("#authPage").hide("drop");
}

function slideSwitch() {
  var nimg =  $('#editorSlide IMG').length;
  if (nimg < 2)
    return;

  var $active = $('#editorSlide IMG.active');

  if ( $active.length == 0 ) $active = $('#editorSlide IMG:last');

  var $next =  $active.next().length ? $active.next()
  : $('#editorSlide IMG:first');

  $active.addClass('last-active');
      
  $next.css({opacity: 0.0})
  .addClass('active')
  .animate({opacity: 1.0}, 500, function() {
      $active.removeClass('active last-active');
  });
}

$("#uploadImagesButton").click(function () {
  showUploadImages();
});

$("#uploadBackButton").click(function () {
  refreshImages($( "#dbImageList" ));
  showMain();
});

$("#authBackButton").click(function () {
  refreshImages($( "#dbImageList" ));
  showMain();
});

$("#authButton").click(function () {
  showAuth();
});

$("#jobsButton").click(function () {
  setupJobsPane();
  showJobs();
});

$("#jobsBackButton").click(function () {
  showMain();
});

$( "#deleteImagesButton").click(function() {
  var selectedImages = [];
  $('#dbImageList .ui-selected').each(function(){
    var imgid =  $(this).children("img").attr("dbid");
    if (jQuery.type(imgid) != 'undefined')
    {
      selectedImages.push(imgid);
    }
  });
  
  if (selectedImages.length == 0)
    return;

  $.post('../image', 
    {deleteImagesList:JSON.stringify(selectedImages)}, 
    function(response) {}, 'json');
  
  refreshImages($( "#dbImageList" ));
});

function sortList (mylist)
{
  var listitems = mylist.children('li').get();
  listitems.sort(function(a, b) {
    return $(a).text().toUpperCase().localeCompare($(b).text().toUpperCase());
  });
  $.each(listitems, function(idx, itm) { mylist.append(itm); });
}

$( "#editButton" ).click(function() {
  // pre-populate title spew box
  populateSpew();
  var selectedImages = [];
  $('#dbImageList .ui-selected').each(function(){
    var imgid =  $(this).children("img").attr("dbid");
    if (jQuery.type(imgid) != 'undefined')
    {
      selectedImages.push(imgid);
    }
  });
  
  if (selectedImages.length == 0)
    return;

  $("#editorSlide").html("");
  $("#flickrSets").tagit("removeAll");
  $("#flickrGroups").tagit("removeAll");
  $("#editTags").tagit("removeAll");
  
  var winWidth =  $(window).width();
  var winHeight = $(window).height();
  var windowAr = winWidth/winHeight;

  var authDict = {};
  
  $.ajax({
    url: "../auth",
    async: false,
    dataType: "json",
    data: {"authStatus":0},
    success: function(json) {
      for (var a in json)
      {
        authDict[a] = json[a];
      }
    }
  });
  
  if (!("flickr" in authDict))
    authDict["flickr"] = false;
  
  if (!("tumblr" in authDict))
    authDict["tumblr"] = false;
  
  if (!("facebook" in authDict))
    authDict["facebook"] = false;

  if (!("twitter" in authDict))
    authDict["twitter"] = false;  

  if (authDict["flickr"]==true)
  {
    $("#flickrOpts").show();
    // flickr is default - don't make it uncheckable for now
//     $("#flickrCheck").prop('disabled', true);
  }
  else
  {
    $("#flickrOpts").hide();
  }

  // Create services button
  for (var service in authDict)
  {
    var serviceId = service + "Check";
    
    if (authDict[service] != true)
    {
      $("#" + serviceId).prop('checked', false);
      $("#" + serviceId).prop('disabled', true);
      $("#" + serviceId).hide();
    }
    else
    {
      $("#" + serviceId).prop('checked', true);
      $("#" + serviceId).prop('disabled', false);
      $("#" + serviceId).show();
    }

  }
  
  
  if (authDict["flickr"] == true)
  {

    var flickrSetsList = [];
    var flickrSetsDict = {};
    
    $.ajax({
      url: "../flickr",
      async: false,
      dataType: "json",
      data: {"getSets":0},
      success: function (response) {
        for (var key in response)
        {
          flickrSetsList.push(response[key]);
          flickrSetsDict[key] = response[key];
        }
      }
    });

    $("#editorSlide").data('flickrSetsList', flickrSetsList);
    $("#editorSlide").data('flickrSetsDict', flickrSetsDict);
    
    $("#flickrSets").tagit({
      availableTags : $("#editorSlide").data('flickrSetsList')
    });
 
    var flickrGroupsList = [];
    var flickrGroupsDict = {};
    
    $.ajax({
      url: "../flickr",
      async: false,
      dataType: "json",
      data: {"getGroups":0},
      success: function (response) {
        for (var key in response)
        {
          flickrGroupsList.push(response[key]);
          flickrGroupsDict[key] = response[key];
        }
      }
    });
    
    $("#editorSlide").data('flickrGroupsList', flickrGroupsList);
    $("#editorSlide").data('flickrGroupsDict', flickrGroupsDict);
    
    $("#flickrGroups").tagit({
      availableTags : $("#editorSlide").data('flickrGroupsList')
    });
  }
  
  $.ajax({
    type: 'POST',
    url: '../image',
    data: {selectedList:JSON.stringify(selectedImages)},
    dataType: 'json',
    async:false,
    success: function(response) {    
      $.each(response.imageList, function (index, image) {
        var img = $('<img id="dynamic">');
        img.attr('src', image.url);
        img.attr('owidth', image.width);
        img.attr('oheight', image.height);
        var imgAr = image.width/image.height;
        
        if(imgAr>windowAr)
        {
          img.attr('height', winHeight);
        }
        else
        {
          img.attr('width', winWidth);
        }
        $('#editorSlide').append(img);
      });
      
      if (response.title != "")
      {
        $("#editTitle").text(response.title);
      }
      else
      {
        $("#editTitle").text("Title");
      }
      
      if (response.description != "")
      {
        $("#editDescription").text(response.description);
      }
      else
      {
        $("#editDescription").text("Description");
      }
      
      if (response.tags != "")
      {
        $.each(response.tags, function (index, tag) {
          $("#editTags").tagit("createTag", tag);
        });        
      }
      
      //turn these into generic function yaaa
      if (response.flickrSets != "")
        setSelectedFlickrSets(response.flickrSets);
      
      if (response.flickrGroups != "")
        setSelectedFlickrGroups(response.flickrGroups);

      if (response.jobDict != "")
      {
        for (var service in response.jobDict)
        {
          if (service == "flickr")
            $("#" + service + "Check").prop('disabled', true);
          
          $("#" + service + "Check").prop('checked', response.jobDict[service]);
          // state has been set, now create button
          $("#" + service + "Check").button();
        }
      }
      
      $( "#otherOpts" ).buttonset();

      $("#latitude").val(response.latitude);
      $("#longitude").val(response.longitude);
      $("#geoCode").prop('checked', response.geoCode);      
    }
  });   
  
  $("#editorSlide").data('authDict', authDict);
  $("#editorSlide").data('titleDirty', false);
  $("#editorSlide").data('descriptionDirty', false);
  $("#editorSlide").data('tagsDirty', false);
  $("#editorSlide").data('flickrSetsDirty', false);
  $("#editorSlide").data('flickrGroupsDirty', false);
  $("#editorSlide").data('otherOptsDirty', false);
  $("#editorSlide").data('geoCodeDirty', false);
  
  $("#templateShow").show();
  $(".templateEdit").hide();
  $("#editBox").data("selectedImages", selectedImages);
  
  $("#standardOptsShow").hide();
  $("#standardOpts").show();
  $("#servicesOptsShow").hide();
  $("#servicesOpts").show();
  $("#flickrOptsShow").show();
  $("#flickrOpts").hide();
  $("#geoCodeOptsShow").show();
  $("#geoCodeOpts").hide();
  
  showEditor();
  setupMap();
});

$("#standardOptsShow").click(function () {
  $("#standardOptsShow").hide("fast");
  $("#standardOpts").show("fast");
});

$("#standardOptsHide").click(function () {
  $("#standardOpts").hide("fast");
  $("#standardOptsShow").show("fast");
});

$("#servicesOptsShow").click(function () {
  $("#servicesOptsShow").hide("fast");
  $("#servicesOpts").show("fast");
});

$("#servicesOptsHide").click(function () {
  $("#servicesOpts").hide("fast");
  $("#servicesOptsShow").show("fast");
});

$("#flickrOptsShow").click(function () {
  $("#flickrOptsShow").hide("fast");
  $("#flickrOpts").show("fast");
});

$("#flickrOptsHide").click(function () {
  $("#flickrOpts").hide("fast");
  $("#flickrOptsShow").show("fast");
});

$("#geoCodeOptsShow").click(function () {
  $("#geoCodeOptsShow").hide("fast");
  $("#geoCodeOpts").show("fast");
  //$("#addresspicker_map").addresspicker( "reloadPosition");
  var map = $( "#addresspicker_map" ).addresspicker( "map" );
  google.maps.event.trigger(map, 'resize');
});

$("#geoCodeOptsHide").click(function () {
  $("#geoCodeOpts").hide("fast");
  $("#geoCodeOptsShow").show("fast");
});

$( "#templateShow" ).click(function() {
  $("#templateShow").hide("fast");
  
  $(".templateEdit").show("fast");
  $("#titleCheck").attr('checked', false);
  $("#descriptionCheck").attr('checked', false);
  $("#tagsCheck").attr('checked', false);
  $("#flickrSetsCheck").attr('checked', false);
  $("#flickrGroupsCheck").attr('checked', false); 
  $("#otherOptsCheck").attr('checked', false);
  $("#geoCodeCheck").attr('checked', false);
  $("#saveTemplateName").val("");
  
  updateTemplateList();
});

$( "#templateHide").click(function () {
  $(".templateEdit").hide("fast");
  $("#templateShow").show("fast");
});

$("#submitLoadTemplate").click(function() {
  var selectedTemplates = getSelectedTemplates();
  

  //var toLoad = $("#templateList").selectedValues();
  
  for (var i = 0; i < selectedTemplates.length; i++)
  {
    $.ajax({
      url: "../template",
      async: false,
      dataType: "json",
      data: {getTemplate:selectedTemplates[i]},
      success: function( data ) { 
        var title = data.title;
        if (title != undefined)
        {
          $("#editTitle").text(title);
          $("#editorSlide").data('titleDirty', true);
        }
        
        var description = data.description;
        if (description != undefined)
        {
          $("#editDescription").text(description);
          $("#editorSlide").data('descriptionDirty', true);
        }
        
        var tags = data.tags;
        if (tags != undefined)
        {
          var tagSet = JSON.parse(tags);
          for (var i = 0; i < tagSet.length; i++) 
          {
            $("#editTags").tagit("createTag", tagSet[i]);
            $("#editorSlide").data('tagsDirty', true);
          }
        }
        
        var flickrSets = data.flickrSets;
        if (flickrSets != undefined)
        {
          var flickrSetsArray = JSON.parse(flickrSets);
          setSelectedFlickrSets(flickrSetsArray);
          $("#editorSlide").data('flickrSetsDirty', true);
        }
        
        var flickrGroups = data.flickrGroups;
        if (flickrGroups != undefined)
        {
          var flickrGroupsArray = JSON.parse(flickrGroups);
          setSelectedFlickrGroups(flickrGroupsArray);
          $("#editorSlide").data('flickrGroupsDirty', true);
        }
        
        var geoCode = data.geoCode;
        if (geoCode != undefined)
        {
          $("#editorSlide").data('geoCodeDirty', true);
          $("#geoCode").prop('checked', geoCode);
          geoCodeSetEnabled(geoCode);      
        }
        
        var latitude = data.latitude;
        if (latitude != undefined)
        {
          $("#latitude").val(latitude);
        }
        
        var longitude = data.longitude;
        if (longitude != undefined)
        {
          $("#longitude").val(longitude);
        }
      }
      
    });
  
  }
  
});

$("#submitSaveTemplate").click(function() {
  var templateDict = {};
  var titleChecked = $("#titleCheck").is(':checked');
  var descriptionCheck = $("#descriptionCheck").is(':checked');
  var tagsCheck = $("#tagsCheck").is(':checked');
  var flickrSetsCheck = $("#flickrSetsCheck").is(':checked');
  var flickrGroupsCheck = $("#flickrGroupsCheck").is(':checked');
  var geoCodeCheck =$("#geoCodeCheck").is(':checked');
  var otherOptsCheck = $("#otherOptsCheck").is(':checked');
  
  var templateName = $("#saveTemplateName").val();
  if (templateName == "")
    return;
  
  templateDict["saveTemplate"] = templateName;
  
  //alert(titleChecked + "," + descriptionCheck + "," + tagsCheck);
  
  if (titleChecked)
  {
    var title = $("#editTitle").html();
    templateDict["title"] = title;
  }
  
  if (descriptionCheck)
  {
    var description = $("#editDescription").html();
    templateDict["description"] = description;
  }
  
  if (tagsCheck)
  {
    var tags = $("#editTags").tagit("assignedTags");
    templateDict["tags"] = JSON.stringify(tags);
  }
  
  if (flickrSetsCheck)
  {
    var flickrSets = getSelectedFlickrSets();
    templateDict["flickrSets"] = JSON.stringify(flickrSets);
  }
  
  if (flickrGroupsCheck)
  {
    var flickrGroups = getSelectedFlickrGroups();
    templateDict["flickrGroups"] = JSON.stringify(flickrGroups);    
  }
  
  if (geoCodeCheck)
  {
    templateDict["geoCode"] = $("#geoCode").is(":checked");
    templateDict["latitude"] = $("#latitude").val();
    templateDict["longitude"] = $("#longitude").val();
  }

  $.ajax({
    url: "../template",
    async: true,
    dataType: "json",
    data: templateDict,
    success: function( data ) { updateTemplateList(); }
  });
  
});

function updateTemplateList()
{
  $.ajax({
    url: "../template",
    async: false,
    dataType: "json",
    data: {"templateList":0},
    success: function( response ) {
      $("#templateList").html("");
      for (var key in response)
      {
        var li = $('<li>');
        li.attr('class','ui-widget-content')
        li.attr('value',key);
        li.text(response[key]);
        $('#templateList').append(li);
      }
    }
  });
}

function setSelectedFlickrSets(flickrSets)
{
  var flickrSetsDict = $("#editorSlide").data("flickrSetsDict");
  for (var i = 0; i < flickrSets.length; i++) 
  {
    $("#flickrSets").tagit("createTag", flickrSetsDict[flickrSets[i]]);
  }
}

function setSelectedFlickrGroups(flickrGroups)
{
  var flickrGroupsDict = $("#editorSlide").data("flickrGroupsDict");
  for (var i = 0; i < flickrGroups.length; i++) 
  {
    $("#flickrGroups").tagit("createTag", flickrGroupsDict[flickrGroups[i]]);
  }
}

function getSelectedFlickrSets()
{
  var flickrSets = [];
  var flickrSetsRaw = $("#flickrSets").tagit("assignedTags");
  var flickrSetsDict = $("#editorSlide").data("flickrSetsDict");
  for (var i = 0; i< flickrSetsRaw.length; i++)
  {
    flickrSets.push(reverseDictLookup(flickrSetsDict, flickrSetsRaw[i]));
  }  
  return flickrSets;
}

function getSelectedFlickrGroups()
{
  var flickrGroups = [];
  var flickrGroupsRaw = $("#flickrGroups").tagit("assignedTags");
  var flickrGroupsDict = $("#editorSlide").data("flickrGroupsDict");
  for (var i = 0; i< flickrGroupsRaw.length; i++)
  {
    flickrGroups.push(reverseDictLookup(flickrGroupsDict, flickrGroupsRaw[i]));
  }  
  return flickrGroups;
}

function getSelectedTemplates()
{
  var selectedTemplates = [];
  $("#templateList .ui-selected").each(function(){
    var templateId =  $(this).attr("value");
    selectedTemplates.push(templateId);
  }); 
  return selectedTemplates;
}

$( "#applyEditsButton" ).click(function() {
  
  //   teardown
  var title = $("#editTitle").html();
  var description = $("#editDescription").html();
  var selectedImages = $("#editBox").data("selectedImages");
  var tags = $("#editTags").tagit("assignedTags");
  
  var titleDirty = $("#editorSlide").data('titleDirty');
  var descriptionDirty = $("#editorSlide").data('descriptionDirty');
  var tagsDirty = $("#editorSlide").data('tagsDirty');
  var flickrSetsDirty = $("#editorSlide").data('flickrSetsDirty');
  var flickrGroupsDirty = $("#editorSlide").data('flickrGroupsDirty');
  var otherOptsDirty = $("#editorSlide").data('otherOptsDirty');
  var geoCodeDirty = $("#editorSlide").data('geoCodeDirty');
  var authDict = $("#editorSlide").data("authDict");
  
  //alert(titleDirty + "," + descriptionDirty + "," + tagsDirty);
  var submitDict = {};
  submitDict["submitList"] = JSON.stringify(selectedImages);
  
  if (titleDirty)
    submitDict["title"] = JSON.stringify(title);
  
  if (descriptionDirty)
    submitDict["description"] = JSON.stringify(description);
  
  if(tagsDirty)
    submitDict["tags"] = JSON.stringify(tags);

  if (authDict["flickr"] == true)
  {
    var flickrSets = getSelectedFlickrSets();
    var flickrGroups = getSelectedFlickrGroups();

    if (flickrSetsDirty)
      submitDict["flickrSets"] = JSON.stringify(flickrSets);
    
    if (flickrGroupsDirty)
      submitDict["flickrGroups"] = JSON.stringify(flickrGroups);
  }
  
  if (geoCodeDirty)
  {
    submitDict["geoCode"] = $("#geoCode").is(":checked");
    submitDict["latitude"] = $("#latitude").val();
    submitDict["longitude"] = $("#longitude").val();
  }
  
  //TODO: just dump the otherOpts for now, need proper notification
  //if its dirty and make them templatable
  
  var jobDict = {}  
  jobDict["flickr"] = $("#flickrCheck").is(':checked');
  jobDict["tumblr"] = $("#tumblrCheck").is(':checked');
  jobDict["twitter"] = $("#twitterCheck").is(':checked');
  jobDict["facebook"] = $("#facebookCheck").is(':checked');
  
  var jobDictString = JSON.stringify(jobDict);
  submitDict["jobDict"] = jobDictString;
  
  $.post('../image', 
    submitDict, 
    function(response) {    
      //no-op, probably
    }, 'json');
  
  $("#editorSlide").html("");
  $("#editBox").data("selectedImages", null);
  
  showMain();
});

$( "#cancelEditsButton" ).click(function() {
  //   teardown
  $("#editorSlide").html("");
  $("#editBox").data("selectedImages", null);
  showMain();
});



$("#editTitle").editInPlace({
  callback: function(unused, enteredText) { $("#editorSlide").data('titleDirty', true); return enteredText; },
  show_buttons: true
});

$("#editDescription").editInPlace({
  callback: function(unused, enteredText) { $("#editorSlide").data('descriptionDirty', true); return enteredText; },
  field_type: "textarea",
  show_buttons: true
});


function showCallback(geocodeResult, parsedGeocodeResult){
  $("#editorSlide").data('geoCodeDirty', true);
}


function setupMap()
{
  $("#addresspicker_map").val("");
  var addresspickerMap = $( "#addresspicker_map" ).addresspicker({
    regionBias: "gb",
    updateCallback: showCallback,
    elements: {
      map: "#map",
      lat: "#latitude",
      lng: "#longitude"
    }
  });

  var gmarker = addresspickerMap.addresspicker( "marker");
  gmarker.setVisible(true);
  addresspickerMap.addresspicker( "reloadPosition");
  
  // we need to mark the map dirty if we move it
  google.maps.event.addListener(gmarker, 'dragend', showCallback);
}

function geoCodeSetEnabled(enableGeoCode)
{
  if (enableGeoCode)
  {
    $("#longitude").prop('disabled', false);
    $("#latitude").prop('disabled', false);
    $("#gmap").show("fast");
    
    //$( "#addresspicker_map" ).addresspicker( "reloadPosition");
    var map = $( "#addresspicker_map" ).addresspicker( "map" );
    google.maps.event.trigger(map, 'resize');
  }
  else
  {
    $("#longitude").prop('disabled', true);
    $("#latitude").prop('disabled', true);
    $("#gmap").hide("fast");
  }    
}

$("#geoCode").click(function() {
  $("#editorSlide").data('geoCodeDirty', true);
  if($("#geoCode").is(':checked'))
    geoCodeSetEnabled(true);
  else
    geoCodeSetEnabled(false);
});

$("#flickrSets").tagit({
  placeholderText: "add flickr sets...",
  afterTagAdded: function(event, ui) {
    $("#editorSlide").data('flickrSetsDirty', false);
  },
  afterTagRemoved: function(event, ui) {
    $("#editorSlide").data('flickrSetsDirty', false);
  },
  beforeTagAdded: function(event, ui) {
    var tagLabel = $("#flickrSets").tagit('tagLabel', ui.tag)
    var tagList = $("#editorSlide").data('flickrSetsList');
    if (tagList.indexOf(tagLabel) < 0)
      return false;
  }
});

$("#flickrGroups").tagit({
  placeholderText: "add flickr sets...",
  afterTagAdded: function(event, ui) {
    $("#editorSlide").data('flickrGroupsDirty', false);
  },
  afterTagRemoved: function(event, ui) {
    $("#editorSlide").data('flickrGroupsDirty', false);
  },
  beforeTagAdded: function(event, ui) {
    var tagLabel = $("#flickrGroups").tagit('tagLabel', ui.tag)
    var tagList = $("#editorSlide").data('flickrGroupsList');
    if (tagList.indexOf(tagLabel) < 0)
      return false;
  }
});

$("#editTags").tagit({
  autocomplete: { source: function( request, response ) {
    $.ajax({
      url: "../tags",
      dataType: "json",
      data: {
        searchTags: request.term
      },
      success: function( data ) {
      response( $.map( data.results, function( item ) {
        return {
          label: item,
          value: item
        }
        }));
      }
    });
    },
      minLength: 2 
  },
  placeholderText: "add tags...",
  afterTagAdded: function(event, ui) {
      //console.log(ui.tag);
    $("#editorSlide").data('tagsDirty', true);
  },
  afterTagRemoved: function(event, ui) {
      //console.log(ui.tag);
    $("#editorSlide").data('tagsDirty', true);
  }

});

function populateSpew()
{
  $.ajax({
    url: "../spew",
    async: true,
    dataType: "json",
    data: {"getspew":0,
           "num":10 },
    success: function( response ) {
      var nresp = response.length;
      var html = $("#wordspew ul").html("");
      var base = $("#wordspew ul");
      for (var i=0; i<nresp; i++)
      {
        var li = $('<li>');
        var a = $('<a>');
        a.attr("href", "#");
        a.text(response[i]);
        a.appendTo(li);
        li.appendTo(base);
        a.click(function () {
          $("#editTitle").text($(this).text());
          $("#editorSlide").data('titleDirty', true);
        });
      }
    }
  });
}

$("#spewTitle").click(function () {
  populateSpew();  
});
