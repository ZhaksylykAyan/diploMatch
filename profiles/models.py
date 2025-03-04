from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Skill(models.Model):
    """ Model to store skills """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class StudentProfile(models.Model):
    """ Profile model for students """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
        primary_key=True  # Ensures ID matches User ID
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=255)
    gpa = models.FloatField()
    portfolio = models.URLField(blank=True, null=True)
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    skills = models.ManyToManyField(Skill, blank=True)

    def clean(self):
        """ Ensure students do not select more than 5 skills """
        if self.pk and self.skills.count() > 5:
            raise ValidationError("Students can select a maximum of 5 skills.")

    def update_profile_completion(self):
        """ Update is_profile_completed after all fields are assigned """
        if not self.user:
            return
        required_fields = [self.first_name, self.last_name, self.specialization, self.gpa]
        if all(required_fields) and self.skills.exists():
            self.user.is_profile_completed = True
        else:
            self.user.is_profile_completed = False
        self.user.save()

    def save(self, *args, **kwargs):
        self.full_clean()  # Validate before saving
        super().save(*args, **kwargs)  # Save first to get an ID
        self.update_profile_completion()  # Update after saving

    def __str__(self):
        return f"{self.user.email} (Student)"

class SupervisorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="supervisor_profile",
        primary_key=True  # Ensures ID matches User ID
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    degree = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    skills = models.ManyToManyField(Skill, blank=True)

    def clean(self):
        """ Ensure supervisors do not select more than 10 skills """
        if self.pk and self.skills.count() > 10:
            raise ValidationError("Supervisors can select a maximum of 10 skills.")

    def update_profile_completion(self):
        """ Update is_profile_completed after all fields are assigned """
        required_fields = [self.first_name, self.last_name, self.degree]
        if all(required_fields) and self.skills.exists():
            self.user.is_profile_completed = True
        else:
            self.user.is_profile_completed = False
        self.user.save()

    def save(self, *args, **kwargs):
        self.full_clean()  # Validate before saving
        super().save(*args, **kwargs)  # Save first to get an ID
        self.update_profile_completion()  # Update after saving

    def __str__(self):
        return f"{self.user.email} (Supervisor)"

class DeanOfficeProfile(models.Model):
    """ Profile model for Dean's Office """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dean_office_profile",
        primary_key=True  # Ensures ID matches User ID
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    job_role = models.CharField(max_length=50, choices=[("manager", "Manager"), ("dean", "Dean")])
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def update_profile_completion(self):
        """ Update is_profile_completed after all fields are assigned """
        required_fields = [self.first_name, self.last_name, self.job_role]
        if all(required_fields):
            self.user.is_profile_completed = True
        else:
            self.user.is_profile_completed = False
        self.user.save()

    def save(self, *args, **kwargs):
        self.full_clean()  # Validate before saving
        super().save(*args, **kwargs)  # Save first to get an ID
        self.update_profile_completion()  # Update after saving

    def __str__(self):
        return f"{self.user.email} (Dean Office)"
