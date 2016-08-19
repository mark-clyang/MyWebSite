from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Pool(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

class Choice(models.Model):
    pool = models.ForeignKey(Pool)
    choice = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

class Post(models.Model):
    author = models.ForeignKey(User)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()
        
    def __str__(self):
        return self.title
        
#sysem messages which shown on home page
class messages(models.Model):
    m_id = models.AutoField(primary_key=True)
    message = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    remarks = models.CharField(max_length=200,blank=True)

#places regulation...
class place(models.Model):
    place_no = models.AutoField(primary_key=True)
    name  = models.CharField(max_length=40)
    section = models.CharField(max_length=40,blank=True,null=True)
    location = models.CharField(max_length=60)
    regulation = models.TextField(blank=True)
    place_groups = models.CharField(max_length=20,blank=True)

#sysadmin 
class members(models.Model):
#    ID  using the system default
    User_id = models.CharField(max_length=20)
    User_name = models.CharField(max_length=20)
    User_password = models.CharField(max_length=20)
    User_right = models.IntegerField()
    allowed = models.BooleanField()


#users...
class who(models.Model):
    u_id = models.AutoField(primary_key=True)
    s_id = models.CharField(max_length=12)
    name = models.CharField(max_length=12)
    email = models.CharField(max_length=60)
    phone = models.CharField(max_length=14)
    department = models.CharField(max_length=60)
    passwd = models.CharField(max_length=12)
    allowed = models.BooleanField(blank=True)
    br_date = models.DateField(blank=True,null=True)


#place reserve records...
#"r_id","place_no","u_id","remarks","approve","start_date","end_date","application"
class reserve(models.Model):
    r_id = models.AutoField(primary_key=True)
    place_no = models.ForeignKey('place')
    u_id = models.ForeignKey('who')
    remarks = models.CharField(max_length=200,blank=True)
    approve = models.IntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    application = models.CharField(max_length=200)
        