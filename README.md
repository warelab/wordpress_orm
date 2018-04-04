# wordpress-orm
An object-oriented Python wrapper around the WordPress JSON API.

Aims for this module:

* Behave as an ORM. Queries return Python classes (e.g. a `Post` class), which then knows how to retrieve related objects (e.g. `User`).
* Tightly wrapped around the Python `requests` package, (though usage does not depend on knowing anything about it).
* Unapologetically Python 3.x only.
* Written specifically against v2 of the WordPress JSON API, and specifically WordPress 4.7+.

This is a work in progress! The most significant feature not yet implemented is authentication.

## Examples

Create an object that contains connection information to the WordPress site. All interaction will occur through this `API` object.

```
import wordpress_orm as wp

# set up the connection
api = wp.API(url="https://demo.wp-api.org/wp-json/")
```

