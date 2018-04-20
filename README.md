# wordpress_orm
An object-oriented Python wrapper around the [WordPress JSON API](https://developer.wordpress.org/rest-api/).

Aims for this module:

* Behave as an ORM (object-relational model). Queries return Python classes (e.g. a `Post` class), which then knows how to retrieve related objects (e.g. `post.users` returns a list of  `User` objects).
* Tightly wrapped around the Python [Requests](http://docs.python-requests.org/en/master/) package, though usage does not depend on knowing anything about it.
* Unapologetically Python 3.x only.
* Written specifically against v2 of the WordPress JSON API, and specifically WordPress 4.7+.

This is a work in progress! The most significant feature not yet implemented is authentication. This is in active development (and being used in code), but should be considered "alpha" quality. Anything may change at any time.

## Examples

##### Connecting to the API

Create an object that contains connection information to the WordPress site. All interaction will occur through this `wordpress_orm.API` object.

```
import wordpress_orm as wp

# set up the connection
api = wp.API(url="https://demo.wp-api.org/wp-json/")
```

The Python objects (e.g.available properties) are closely tied to the WordPress API; keeping the [reference page](https://developer.wordpress.org/rest-api/reference/) open as you code will be handy.

##### Retrieving Posts

Use the `PostRequest` object to retrieve posts from the API. Below we create a new `PostRquest` directly from the `api` object (which contains the connection information). We will retrieve all posts from the category "News" by specifying the slug for that category ('news').

```
post_request = api.PostRequest()
post_request.categories = ['news']
posts = post_request.get() # empty list returned if none found
```

The [post API arguments](https://developer.wordpress.org/rest-api/reference/posts/#arguments) are all defined in the `PostRequest` Python object. For example, we can limit the posts to the most recent three:

```
post_request = api.PostRequest()
post_request.categories = ['news']
post_request.per_page = 3
post_request.orderby = "date"
post_request.order = "desc"
posts = post_request.get()
```

##### Accessing Entity Elements

`wordpress_orm` defines Python classes for each WordPress entity: `Post`, `PostRevision`, `Category`, `Tag`, `Page`, `Comment`, `Taxonomy`, `Media`, `User`, `PostType`, `PostStatus`, `Setting`. The WordPress API defines a schema for each entity. For example, the [posts schema](https://developer.wordpress.org/rest-api/reference/posts/#schema) defines `title`, `author`, and `category`. 

`wordpress_orm` defines a schema property `s` through which you can access each element. For example, if you have a `post` object as retrieved above, you can access the title as returned by the API with:

```
print(post.s.title)
```

Similarly, the author can be accessed:

```
print(post.s.author)
```

However, this is not very useful: the value returned by the API here is the author ID (just an integer). The `Post` object has a property named `author` that returns an `User` Python object; behind the scenes, another API call will be made to create the entity.

```
# get the name of the author from a post
print("{0} {1}".format(post.author.s.first_name, post.author.s.first_name))
```

This is the reason for the `s` property: it keeps the WordPress schema properties in a separate name space from more user(Python)-friendly properties, even if they share the same name. For example:

```
>>> post.s.categories
[1,6]
>>> post.categories
<WP Category 
```

## Caveats

The WordPress API is a wrapper around PHP functions that are part of WordPress. Ideally the API would not expose this detail, but there are a few holes in the documentation (and the API for that matter) that require one to reference the underlying code. The information below is useful for a developer of `wordpress_orm` and should help when dealing with these cases. Any user of the code can ignore this section.

##### `User` Queries

The [`search` parameter](https://developer.wordpress.org/rest-api/reference/users/#arguments) of the `User` query is documented as “Limit results to those matching a string.” but doesn't provide further detail. The underlying code is a PHP function called [WP_User_Query](https://codex.wordpress.org/Class_Reference/WP_User_Query) that tries to guess which column to search ([actual code here](https://github.com/WordPress/WordPress/blob/921e131eae45801b8fdb1ecfceb5d7839fdfd509/wp-includes/class-wp-user-query.php#L524-L533)). It takes an additional parameter called `search_columns` to specificy which columns to search. Possible values are:

* `ID` - Search by user id.
* `user_login` - Search by user login.
* `user_nicename` - Search by user nicename.
* `user_email` - Search by user email.
* `user_url` - Search by user url.


In practice, `search_columns` apprears to be ignored via the API.


GitHub issue: WP-API/docs#26 ([link](https://github.com/WP-API/docs/issues/26)).