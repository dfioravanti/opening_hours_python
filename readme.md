# Readme

## How to run

The project provides a dockerfile so that it is possible to
1. build the image with a
```
docker build --tag hours --file Dockerfile .
```
2. run the app with
```
docker run -p 8000:8000 hours 
```
3. send in a test example with
```
curl -H "Content-Type: application/json" --data @./data/full_test.json http://localhost:8000/prettify
```
## Missing specifications and implementation choices

While implementing the project I faced a series of arbitrary choices as the specification did not go into that particular
detail. 
All of them are arbitrary and questionable in a real world application. 
I tried to strike a good balance between maximum usability for the end user and the enforcement of some sane behavior.

* The specification did not say what to do in case of replicated keys in the JSON.
  The implementation uses the standard python behavior of overwriting identical keys.
* The specification did not say what to do in case of repeated opening and closing. 
  The implementation return a 422 (Unprocessable Entity) status code.
* The specification did not say how to deal with missing days in the JSON.
  The implementation interprets a missing day as a closed day.
* The specification did not say if it is possible for a restaurant to not close for a day.
  The implementation assumes that this is not possible as it is complex to represent in the chosen pretty format.
* The specification does not say what to do with overlapping opening and closing. 
  The implementation ignores this
* The specification does not say what to do with semantically invalid inputs. 
  The implementation ignore this problem with the exception that it sorts the inputs by day and by time so there cannot be a closure happening before an opening. 
  But for example `1 AM - 3 AM, 2 AM - 4 AM` is a valid output for a valid input.

## Problems with the input format

The input format presents a series of problem which in one sentence can be boiled down to: It is both hard to read for humans and hard to parse for machines.

The problem for humans is clear: compute the number of seconds from midnight is not an easy task.  
For parsing the two most annoying elements are
1. In order to know the close time for one day it can happen that we need to check the day after. This forces some bookkeeping logic that feels unnecessary.
  In particular it gets a bit messy when one considers that a week is circular so now to process a close time on Monday night one has to wait until the end of the week when Sundays' entries are processed.
2. The fact that weekday is a key instead of a field makes it impossible to create a general schema that works for each day. For example pydantic cannot represent the input JSON so it cannot be process by FastAPI automatically.

## Alternative input formats

As alternative input format I would propose something like
```
{
  "opening_day": depends
  "opening_time": depends
  "closing_day": depends
  "closing_time": depends
}
```
where the specific types used for day and time can change according to the constrains
* If human readability is important and we do not care about been space efficient we can use a string for the day and a `{"hour": int, minute: int, second: int}` object for the time.
* If the message size is important we can use a 0-6 integer for the day and a int for the timestamp as seconds from the midnight
* If the message size is really important we can encode the day and time inside the timestamp as `SECONDS_IN_DAY * DAY_NUMBER + TIME_AS_SECOND_FROM_MIDNIGHT`. Then recovering the information is just a matter of repeated divisions.

### Advantages

Compared with the proposed input format this format has the following advantages:
* Check is every opening as a closure is not trivial
* There is a standardized schema for each entry so parsing it with automatic tools is rally easy.
* It can be optimized to be human readable or machine efficient.

### Limitations

The new format still shares some limitations with the old one. 
In particular it still cannot anything to help us with semantically invalid inputs. 
So for example `1 AM - 3 AM, 2 AM - 4 AM` would still be a valid output.