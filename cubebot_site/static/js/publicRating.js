$(document).ready(function() {
  var myUserID = '{{ userID }}';
  var myReviewerID = '{{ reviewer }}';
  // var rateValue;
  var rateText = "";

$("#submitReview").click(function() {
  if($('#ratingRequired').is(":visible")) {
    $("#ratingRequired").toggleClass('hidden');
  };
  // alert("submit button clicked");
  // alert(myUserID);
  // alert(rateValue);
  // alert(rateText);
  var myStarRating = rating.value;
  // alert(myStarRating);
  if (myStarRating == -1) {
    // alert("Please select star rating then press submit.");
    $("#ratingRequired").toggleClass('hidden');
    return;
  };
  // if ( typeof rateValue == 'undefined') {
  //   alert("Doh, looks like you forgot to rate it!");
  //   $("#ratingRequired").toggleClass('hidden');
  //   return;
  // };
  var contentThID = "homepageItem1";
  var myContentID = -1;
  var myContentTitle = "homepageItemTitle1";
  // alert(contentThID);
  var friendID = "public";

  var reviewData = {
    "userID": "homepage",
    "thoughtsON": contentThID,
    "thoughtValue": myStarRating,
    "thoughtTitle": myContentTitle,
    "friend": friendID,
    // "image_url2": imageUrl // just console testing for messenger share
  };

    $.ajax({
        type : "POST",
        url : "/_load_ajax_review",
        data: JSON.stringify(reviewData),
        contentType: 'application/json',
        success: (function () {
          window.location.href = "https://aa75436e.ngrok.io/content/thoughtson/public";
          // $('#exampleModal').modal('show');
          // var loadURL = "https://aa75436e.ngrok.io/content/thoughtson/public";
          // $('#exampleModal').modal('show').find('.modal-content').load(loadURL);
          // $("#ratingFeedback").toggleClass('hidden');
      })
      });

  });
});

$(document).ajaxStop(function() {
        // place code to be executed on completion of last outstanding ajax call here
        // alert("ajax Call completed");
  });
