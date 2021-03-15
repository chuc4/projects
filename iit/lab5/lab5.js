/* Lab 5 JavaScript File
   Place variables and functions in this file */

function validate(formObj) {
   // put your validation code here
   // it will be a series of if statements

   if (formObj.firstName.value == "") {
      alert("You must enter a first name");
      formObj.firstName.focus();
      return false;
   }

   if (formObj.lastName.value == "") {
      alert("You must enter a last name");
      formObj.lastName.focus();
      return false;
   }

   if (formObj.title.value == "") {
      alert("You must enter a title");
      formObj.title.focus();
      return false;
   }

   if (formObj.org.value == "") {
      alert("You must enter an organization");
      formObj.org.focus();
      return false;
   }

   if (formObj.nickname.value == "") {
      alert("You must enter a nickname");
      formObj.nickname.focus();
      return false;
   }

   if (formObj.comments.value == "") {
      alert("You must enter comments");
      formObj.comments.focus();
      return false;
   }
   alert("Success!");
   return true;
}

function clearBox() {
   var box_input = document.getElementById("comments").value;
   if (box_input == "Please enter your comments") {
   document.getElementById("comments").value = "";
  }
}
function findNickname() {
   var found_nick = document.getElementById("nickname").value;
   var found_first = document.getElementById("firstName").value;
   var found_last = document.getElementById("lastName").value
   alert(found_first + " " + found_last + " is " + found_nick);
}
