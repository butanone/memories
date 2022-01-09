# Memories
#### Video Demo:  https://youtu.be/EUZNfyf32U4
#### Description:
This is a web application called memories. It is like a shared journal, where the idea is that users add their friends and post an account of a memory that they share to their page.
It uses flask, with a central application.py file instructing the backend and interaction with the database, and some helper functions in helpers.py.

The database consists of three tables; users, which contains each user's username and password hash; friends, which contains pairs of usernames representing friends along with date, time of request and a boolean epxressing whether the friend request has been accepted; posts, which contains the post content, date, time, and a boolean expressing whether it has been approved.

The most challenging part was to think of the best and most efficient way to get the friends table to work, because of the nature of having two friends being friends with each other. When searching for a user's friends or friend requests, it is necessary to search BOTH friend username columns, which feels a bit tedious. Also, there was no way of knowing where each friend would get stored so I decided to store them alphabetically and store the name of the friend requester in order that friend requests be rendered correctly.

The first step, is to add friends in addfriends.html, which uses jQuery to search the database for users whose name starts with the current user's input and dynamically generate 'add friend' buttons on the page. This then writes to the 'friends' table in the database
The recipient will then see a notification badge next to their 'friend requests' (/friend_requests.html) link, which, when accessed, generates a table with all of the user's friend requests which are yet to be approved, the date, time, and the option to accept or decline them.
Once they have accepted a friend, they will then see their friends listed on friends.html in a table with the option to delete them at any point.
Having friends allows the user to post memories to their page on the post memories page (/postmemories). This page uses javascript, jquery to dynamnically show the sender's friends' names as the user types, appends them to the page once the sender clicks the add button, and sends the memory to the recipient. This was possibly the most challenging part of making the whole application, because not only did it involve dynamnically generating multiple elements using javascript and jquery, but it also needed to use the values from multiple dynamically generated elements (the friends to whom the memory would be sent) in the form!
The recipient, in their post requests page (/post_requests) can choose to accept or delete this memory - and once it is accepted,will appear on their homepage, index.html.
I decided to keep the design reasonably minimalistic because of the wide demographic who could potentially use this application.