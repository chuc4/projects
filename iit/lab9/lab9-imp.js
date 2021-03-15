$(document).ready(function() {
   $.ajax({
      type: "GET",
      url: "../lab9-projects.json",
      dataType: "json",
      success: function(responseData, status) {
         var output = "<ul>";
         //create loop to iterate through json file

          $.each(responseData.menuItem, function(i, item) {
            output += '<li><a href="'+item.menuURL+'">"'+item.menuName+ " "+item.menuDesc+'"</a></li>';
          });
          output +="</ul>";
          $('#projects').html(output); //projects id in html file

          img_output = "<img";

          $.each(responseData.description2, function(i, item) {
            img_output += ' src="'+item.imgURL+'" alt="'+item.imgName+'" width="'+item.imgWidth+'" height="'+item.imgHeight+'" + ';
         });
         img_output+="/>";
         $('#lab2_images').html(img_output);

         img_output = "<img";
         $.each(responseData.description4, function(i, item) {
            img_output += ' src="'+item.imgURL+'" alt="'+item.imgName+'" width="'+item.imgWidth+'" height="'+item.imgHeight+'" + ';
         });
         img_output+="/>";
         $('lab4_images').html(img_output);

         img_output = "<img";
         $.each(responseData.description5, function(i, item) {
            img_output += ' src="'+item.imgURL+'" alt="'+item.imgName+'" width="'+item.imgWidth+'" height="'+item.imgHeight+'" + ';
         });
         img_output+="/>";
         $('lab5_images').html(img_output);

         img_output = "<img";
         $.each(responseData.description6, function(i, item) {
            img_output += ' src="'+item.imgURL+'" alt="'+item.imgName+'" width="'+item.imgWidth+'" height="'+item.imgHeight+'" + ';
         });
         img_output+="/>";
         $('lab6_images').html(img_output);
      }
   });
});
