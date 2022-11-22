# django-easy-audit

Yet another Django audit log app, hopefully the easiest one.

This app allows you to keep track of every action taken by your users.

## Quickstart

1. Install Django Easy Audit by running `pip install django-easy-audit`.

   * Alternatively, you can download the [latest release](https://github.com/soynatan/django-easy-audit/releases) from GitHub, unzip it, and place the folder 'easyaudit' in the root of your project._

2. Add 'easyaudit' to your `INSTALLED_APPS` like this:

   ```python
   INSTALLED_APPS = [
       ...
       'easyaudit',
   ]
   ```

3. Add Easy Audit's middleware to your `MIDDLEWARE` (or `MIDDLEWARE_CLASSES`) setting like this:

   ```python
   MIDDLEWARE = (
       ...
       'easyaudit.middleware.easyaudit.EasyAuditMiddleware',
   )
   ```

4. Run `python manage.py migrate easyaudit` to create the app's models.

5. That's it! Now every CRUD event on your whole project will be registered in the audit models, which you will be able to query from the Django admin app. Additionally, this app will also log all authentication events and all URLs requested.

## Settings

For an exhaustive list of available settings, please [check our wiki](https://github.com/soynatan/django-easy-audit/wiki/Settings).

Below are some of the settings you may want to use. These should be defined in your project's `settings.py` file:

* `DJANGO_EASY_AUDIT_WATCH_MODEL_EVENTS`

* `DJANGO_EASY_AUDIT_WATCH_AUTH_EVENTS`

* `DJANGO_EASY_AUDIT_WATCH_REQUEST_EVENTS`

  Set these to `False` to stop logging model, authentication, and/or request events.

* `DJANGO_EASY_AUDIT_UNREGISTERED_CLASSES_EXTRA`

  A list of Django models which will be ignored by Django Easy Audit.
  Use it to prevent logging one or more of your project's models.
  List items can be classes or strings with `app_name.model_name` format.

* `DJANGO_EASY_AUDIT_UNREGISTERED_URLS_EXTRA`

  A list of URLs which will be ignored by Django Easy Audit.
  List items are expected to be regular expressions that
  will be matched against the URL path.
  [Check our wiki](https://github.com/soynatan/django-easy-audit/wiki/Settings#request-auditing)
  for more details on how to use it.

* `DJANGO_EASY_AUDIT_CRUD_DIFFERENCE_CALLBACKS`

  May point to a list of callables/string-paths-to-functions-classes in which the application code can determine
  on a per CRUDEvent whether or not the application chooses to create the CRUDEvent or not. This is different
  from the registered/unregistered settings (e.g. `DJANGO_EASY_AUDIT_UNREGISTERED_CLASSES_EXTRA`).
  This is meant to be for dynamic configurations where the application
  may inspect the current save/create/delete and choose whether or not to save that into the database or ignore it.

* `DJANGO_EASY_AUDIT_USER_DB_CONSTRAINT`

  Default is `True`. This is reserved for future use (does not do anything yet). The functionality provided by the
  setting (whether enabled or disabled) could be handled more explicitly in certain
  code paths (or even internally as custom model managers). For projects that separate the easyaudit database, such
  that the tables are not on the same database as the user table, this could help with making certain queries easier.
  Again, this doesn't do anything yet, and if it ever does, the version will be increased and the README will be
  updated accordingly. If you keep your database together (the standard usage), you have nothing to worry about.

* `DJANGO_EASY_AUDIT_CRUD_EVENT_LIST_FILTER`

* `DJANGO_EASY_AUDIT_LOGIN_EVENT_LIST_FILTER`

* `DJANGO_EASY_AUDIT_REQUEST_EVENT_LIST_FILTER`

  Changeview filters configuration.
  Used to remove filters when the corresponding list of data would be too long.
  Defaults are:
    - ['event_type', 'content_type', 'user', 'datetime', ] for CRUDEventAdmin
    - ['login_type', 'user', 'datetime', ] for LoginEventAdmin
    - ['method', 'user', 'datetime', ] for RequestEventAdmin

* `DJANGO_EASY_AUDIT_DATABASE_ALIAS`

  By default it is the Django `default` database alias. But for projects that have split databases,
  this is necessary in order to keep database atomicity concerns in check during signal handlers.

  To clarify, this is only _truly_ necessary for the model signals.
  
* `DJANGO_EASY_AUDIT_CRUD_EVENT_NO_CHANGED_FIELDS_SKIP`

  By default this is `False`, but this allows the calling project not to save `CRUDEvent` if the changed fields as
  determined by the `pre_save` handler sees that there are no changed fields. We are keeping it off by default so that
  projects that wish to use this (potentially less `CRUDEvent`) can choose to turn it on! And those that do not want it (yet or ever),
  or those that do not closely follow the release notes of this project will have one less worry when upgrading.

* `DJANGO_EASY_AUDIT_CHECK_IF_REQUEST_USER_EXISTS`

  By default this is `True`, but this allows the calling project to make easyaudit ignore user validation on audit event creation.
  This is useful when you have a app with soft delete or no delete on users model. With this set to `False`, easyaudit only fetch `request.user` for audit event creation, no db check is made, meaning you can speed up audit events creation and save some DB calls.

* `DJANGO_EASY_AUDIT_READONLY_EVENTS`

  Default is `False`. The events visible through the admin interface are editable by default by a
  superuser. Set this to `True` if you wish to make the recorded events read-only through the admin
  UI.

* `DJANGO_EASY_AUDIT_FIELD_VALUE_RESOLVER_MAP`
  `easyaudit` uses `smart_str` for field values by default, with the exception of DateTimeField. `DJANGO_EASY_AUDIT_FIELD_VALUE_RESOLVER_MAP` extends the ability to customize field values to more fields. The resolver map should be a map of class -> field value resolver. The field value resolver fn will be provided the object and the field.

  An example of the usefulness would be customizing value of FK. Instead of calling `__str__` on the instance, we might want the PK instead.

  def resolve_fk_value(object, field):
  return object.pk

  DJANGO_EASY_AUDIT_FIELD_VALUE_RESOLVER_MAP = {
  ForeignKey: resolve_fk_value
  }

* `DJANGO_EASY_AUDIT_LOGGING_BACKEND`

  A pluggable backend option for logging. Defaults to `easyaudit.backends.ModelBackend`.
  This class expects to have 3 methods:
  * `login(self, login_info_dict):`
  * `crud(self, crud_info_dict):`
  * `request(self, request_info_dict):`

  each of these methods accept a dictionary containing the info regarding the event.
  example overriding:

  ```python
    import logging

    class PythonLoggerBackend:
        logging.basicConfig()
        logger = logging.getLogger('your-kibana-logger')
        logger.setLevel(logging.DEBUG)

        def request(self, request_info):
            return request_info # if you don't need it

        def login(self, login_info):
            self.logger.info(msg='your message', extra=login_info)
            return login_info

        def crud(self, crud_info):
            self.logger.info(msg='your message', extra=crud_info)
            return crud_info
  ```

## Customising model queryset

Sometimes, you want to customise the queryset method used for fetching a specific instance.
For example, when using the [django-softdelete](https://django-safedelete.readthedocs.io/en/latest/) package and you want to record the `undelete` actions.

In order to customise the queryset used, add a method named `get_easyaudit_queryset` to your model. The name of the method can be customized per model by setting the `EASY_AUDIT_QUERYSET_METHOD` attribute to the name of the method to use.

The value should be the name of the model method that returns the needed queryset.

Example:

```python
class MyModel(models.Model):
    ...

    @classmethod
    def get_easyaudit_queryset(cls):
        return cls.objects.all_with_deleted()


# Customize the queryset method used by easyaudit
class MyOtherModel(models.Model):
    EASY_AUDIT_QUERYSET_METHOD = 'get_scoped_queryset'

    ...

    @classmethod
    def get_scoped_queryset(cls):
        return cls.objects.filter(users__count__gt=0, owner__is_active=True)
```

## Using instance metadata

You can leverage the `CRUDChange.metadata` JSON field when you want to save some other related data to each change. For example when aggregating the changes across multiple models by some specific business logic.
To populate this field, you should declare a method on the model that requires it.

The default method name is `get_easyaudit_metadata`, but it can be configured by adding the `EASY_AUDIT_METADATA_METHOD`field on the model.

Example:
```python
class ModelA(models.Model):
    ...

class ModelB(models.Model):
    parent = models.ForeignKey(ModelA, ...)
    
    ...

    def get_easyaudit_metadata(self):
        return dict(model_a_id=self.parent_id)

    ...


class ModelC(models.Model):
    EASY_AUDIT_METADATA_METHOD = "fetch_metadata"
    
    ...
    
    parent = models.ForeignKey(ModelB, ...)

    ...

    def fetch_metadata(self):
        return dict(model_b_id=self.parent_id, model_a_id=self.parent.parent_id)
```

With this setup you can now fetch all changes from `ModelB` and `ModelC`that are related to a specific `ModelA` instance in one query.

## What does it do

Django Easy Audit uses [Django signals](https://docs.djangoproject.com/en/dev/topics/signals/)
to listen to the events happening in your project, such as when a user creates, updates or deletes
a registry. This applies to every model of every app in your project.

When any of these events takes place, Django Easy Audit will log it in the model `CRUDEvent`.
You can query this information in the Django Admin app.

Besides logging CRUD events, Django Easy Audit will log all authentication events (such as when a user logs in, out, or fails to log in) and all the URLs requested in the project. This information is stored in models `LoginEvent` and `RequestEvent`.

## Why you should use it

There are many Django auditing apps out there, but most them require you to change very important
parts of your project's code. For example, they require you to add fields to your models, or make
them inherit from a certain class. Some of them create a mirror for each of your models, which means
duplicate migrations.

It is not that they don't work or that they are not great apps. But in case you need something
easier to set up, and you don't want your code to depend so much on a third-party app, Django Easy Audit
may be your best choice.

The good thing about this app is that it doesn't get in the way. It is [easy and quick to install](https://github.com/soynatan/django-easy-audit/wiki/Installation), and it
begins logging everything right away, without you having to inject code anywhere in your project.

## Contact

Find us on Twitter at [@upliftltd](https://twitter.com/upliftltd),
or send me an email to [opensource@uplift.ltd](mailto:opensource@uplift.ltd).

## Locally install dependencies
* Generate egg information `python setup.py egg_info`
* Install dependencies `pip install -r django_easy_audit.egg-info/requires.txt`

## Run tests locally
* `cd ./easyaudit/tests`
* `python -m manage test`