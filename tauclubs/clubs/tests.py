import json
from django.test import Client, TestCase
from accounts.models import User
from .models import Club, Post
from rest_framework.test import APIClient


# Create your tests here.

class ClubTestCase(TestCase):

    def setUp(self):

        self.admin = User.objects.create_superuser(email="admin@stud.tau.edu.tr", password="admin@123", first_name="Admin", last_name="Super")

        self.user = User.objects.create_user(email="student1@stud.tau.edu.tr", password="pass@123", first_name="user", last_name="user")
        self.manager = User.objects.create_user(email="student2@stud.tau.edu.tr", password="pass@123", first_name="manager", last_name="user")
        self.user2 = User.objects.create_user(email="student3@stud.tau.edu.tr", password="pass@123", first_name="user", last_name="user")

        self.club = Club.objects.create(name="Informatix", manager=self.manager)
    
    def test_create_club(self):
        print("\ntest_create_club")
        response_ = self.client.get('/admin/', follow=True)
        self.response = self.client.login(email="admin@stud.tau.edu.tr", password="admin@123")
   
        self.assertTrue(self.response)
        print("client.login(): " + str(self.response))

        club_data = {
            "name": "Test Club",
            "manager": self.user.id,
            "members": [],
            "pending_members": [],
            "responsibleLecturer": "Test Lecturer",
            "clubMail": "testclub@stud.tau.edu.tr",
            "followers": []
        }

        self.response = self.client.post("/clubs/", data=club_data)
        self.assertEqual(201, self.response.status_code)
        print("POST-Request: " + str(self.response.status_code))

        clubs = Club.objects.all()
        control = [True for id in range(0,len(clubs)) if clubs[id].name == "Test Club"]
        self.assertTrue(True in control)
        print("Neue Club erstellt: " + str(control[0]) + ": " + str(clubs[0]))

    def test_update_club_infos_byadmin(self):
        print("\ntest_update_club_infos_byadmin")
        
        response_ = self.client.get('/admin/', follow=True)
        self.response = self.client.login(email="admin@stud.tau.edu.tr", password="admin@123")

        self.assertTrue(self.response)
        print("client.login(): " + str(self.response))

        data = {"name" : "INFX"}

        self.response = self.client.patch("/clubs/" + str(self.club.id) + "/", data=data, format='json', content_type='application/json')
        clubs = Club.objects.all()
   
        self.assertEqual(200, self.response.status_code)
        print("PATCH-Request: " + str(self.response.status_code))

        self.assertEqual(clubs[self.club.id - 1].name, data['name'])
        print("Aktualisiert: " + str(clubs[self.club.id - 1]))

    def test_membership(self):
        print("\ntest_membership")

        self.response = self.client.login(email='student1@stud.tau.edu.tr',
            password='pass@123')

        self.assertEqual(self.response, True)
        print("client.login(): " + str(self.response))

        self.response = self.client.get("/clubs/" + str(self.club.id) + "/membership/")
        
        self.assertEqual(201, self.response.status_code)
        print("GET-Request: " + str(self.response.status_code))
        self.assertEqual(self.user in self.club.pending_members.all(), True)
        print("Membership Request: " + str(self.user in self.club.pending_members.all()))

    def test_follow(self):
        print("\ntest_follow")
        
        self.response = self.client.login(email='student1@stud.tau.edu.tr',
            password='pass@123')

        self.assertEqual(self.response, True)
        print("client.login(): " + str(self.response))

        self.response = self.client.get("/clubs/" + str(self.club.id) + "/follow/")
        print("GET-Request: " + str(self.response.status_code))

        self.assertEqual(200, self.response.status_code)
        self.assertEqual(self.user in self.club.followers.all(), True)
        print("Followed: " + str(self.user in self.club.followers.all()))

    def test_unfollow(self):
        print("\ntest_unfollow")

        self.response = self.client.login(email='student1@stud.tau.edu.tr',
            password='pass@123')

        self.assertEqual(self.response, True)
        print("client.login(): " + str(self.response))
        
        self.response = self.client.get("/clubs/" + str(self.club.id) + "/unfollow/")
        print("GET-Request: " + str(self.response.status_code))

        self.assertEqual(200, self.response.status_code)
        self.assertEqual(self.user not in self.club.followers.all(), True)
        print("Unfollowed: " + str(self.user not in self.club.followers.all()))

    def test_admit_member(self):
        print("\ntest_admit_member")

        self.response = self.client.login(email='student1@stud.tau.edu.tr',
            password='pass@123')

        self.assertEqual(self.response, True)
        self.response = self.client.get("/clubs/" + str(self.club.id) + "/membership/")
        self.client.logout()

        #Non-Manager login and post request
        print("Non-Manager login and POST-Request")
        self.response = self.client.login(email='student3@stud.tau.edu.tr',
            password='pass@123')

        self.assertEqual(self.response, True)
        print("client.login(): " + str(self.response))
        
        data = {"user" : "2"}

        self.response = self.client.post("/clubs/" + str(self.club.id) + "/admit_member/", data=data, format='json', content_type='application/json')
        print("POST-Request by Non-Manager: " + str(self.response.status_code))
        self.assertEqual(403, self.response.status_code)

        self.client.logout()

        #Manager login and post request
        print("Manager login and POST-Request")
        self.response = self.client.login(email='student2@stud.tau.edu.tr',
            password='pass@123')

        self.assertEqual(self.response, True)
        print("client.login(): " + str(self.response))
        
        data = {"user" : "2"}

        self.response = self.client.post("/clubs/" + str(self.club.id) + "/admit_member/", data=data, format='json', content_type='application/json')
        print("POST-Request by Club Manager: " + str(self.response.status_code))

        self.assertEqual(201, self.response.status_code)
        self.assertEqual(self.user in self.club.members.all(), True)
        self.assertEqual(self.user not in self.club.pending_members.all(), True)
        print("New member: " + str(self.user) + " in Club: " + str(self.club))
     

class PostTestCase(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(email="student4@hotmail.com", password="pass@123", first_name="user", last_name="user")

        self.manager_user = User.objects.create_user(email="student3@hotmail.com", password="pass@123", first_name="manager", last_name="user")
        # self.club = Club.objects.create(name="Informatix", manager=User.objects.create(email = "student3@hotmail.com"))
        self.club = Club.objects.create(name="Informatix", manager=self.manager_user)
        

    #Manager Kontroll

   # def test_managerKontrol(self):

    #    self.response = self.client.login(email='student4@hotmail.com',password='pass@123')

     #   self.assertEqual(self.response, True)

      #  self.response = self.client.get("/clubs/" + str(self.club.id) + "/manager/")
        
       # self.assertEqual(201, self.response.status_code)
        #self.assertEqual(self.user in self.club.manager.all(), True)

    #Post teilen in der Clubseite

    def test_create_post(self):
        print("\ntest_create_post")
    
       # client = APIClient()
       # client.force_authenticate(user=self.user) ## 
        self.response = self.client.login(email='student3@hotmail.com',
            password='pass@123')

        self.assertEqual(self.response, True)
        print("client.login(): " + str(self.response))
        #self.assertEqual(self.club.manager, )
        data = {
                "postId": "1",
                "name": " Club-Technologie",
                "postdate": "2022-12-11",
                "clubname": 1,
                "description": "ilk post",
                "type": "teknoloji"
        }
        self.response = self.client.post('/posts/',data=data) ###
        print("POST-Request: " + str(self.response.status_code))

        self.assertEqual(201, self.response.status_code)
        
        posts = Post.objects.all()
        control = [True for id in range(0,len(posts)) if posts[id].postId == "1"]
        print("Neue Post erstellen: " + str(posts[int(data.get("postId"))-1]))
        self.assertTrue(True in control)
        
        #print("Neue Post erstellen: " + str(posts[int(data.get("postId"))-1]))
        
        
    
    #def test_edit_post(self):
        
     #  data = {'postId': '2', 'name': 'Etkinkik' , 'postdate' :'22.1.23' , 'clubname': 'EMK'}
      # self.response = self.client.put('/posts/1', "data")
        #serializer = PostSerializer(post, data=request.data)
        
       #self.assertEqual(201, self.response.status_code)
       #self.assertEqual(self.user in self.club.Post.objects.all(), True)

   # def test_newmemberInfo_check(self):
        
        # Checking new member information
    #    self.response = self.client.get("/clubs/" + str(self.club.id) + "/pending_members/")
        
     #   self.assertEqual(201, self.response.status_code)
      #  self.assertEqual(self.user in self.club.pending_members.all(), True)

    # Club manager delete and chance members
    
    