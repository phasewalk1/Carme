Since I don't want to spend a lot of time reading and deeply understanding lengthy research papers to implement (a working prototype of) the recommendation engine, I have been spending lots of time researching open-source implementations. 

I think I stumbled upon a really, really good one.
\>> [Deep Hybrid](https://github.com/michaelbzms/DeepRecommendation)

## Overview

[DeepRecommendation](https://github.com/michaelbzms/DeepRecommendation) is an open-source Github repository that contains the source code for *Michael Bizimis*'s **master's thesis**. The code is under an [MIT License](https://github.com/michaelbzms/DeepRecommendation/blob/main/LICENSE), giving us the ability to *modify, and deploy the code in commercial applications*. 

The methodology employed in the extendable *deep hybrid* codebase is that of the **hybrid** model. 

 > 
 >  > 
 >  > "We combine NCF with content-based methods for creating item and user profiles to get a **hybrid** Recommendation System that: *avoids the **cold-start problem** of CF*, and *achieves a **better performance** by learning parameters from features*"

Checkout the repository's README for more relevant information on the scope of the thesis, which outlines three distinct neural network architectures for recommendation systems: **Basic NCF**, **Attention NCF**, and **Graph NCF**.

 > 
 >  > 
 >  > Attention is the magic that makes transformers powerful, and was created by Google. The *Attention NCF* "...constructs the user profiles from item profiles dynamically, instead of using fixed ones. In doing so, it also calculates an attention weight between the candidate item and each rated item."
 >  > [Attention NCF](https://github.com/michaelbzms/DeepRecommendation/tree/main#attention-ncf)

In this document, we will first discuss the dataset used in the experiment and how it compares to our application. Then we'll lay out possible first steps for extending [DeepRecommendation](https://github.com/michaelbzms/DeepRecommendation) to work with our application's data (integration).

## The Datasets Used in the Thesis Experiment

Since we will need to extend **deep hybrid** to work with our application's data, it would be sensible to review the datasets that the code already uses in it's experiments. This will give us an idea of what type of structural data the code is already expecting, and will help us plan what we need to collect in our backend, also, what we may want to modify in the codebase.

The experiments involved in his thesis use datasets that are pretty similar to what we will end up using for our application, though they are focused on movies.

 > 
 >  > 
 >  > "We combined:
 >  > 
 >  > * The **25M MovieLens dataset** with 1-5 ratings from 160000 users to 60000 movies
 >  > * `ratings.csv`
 >  > * The **IMDb database** for **metadata** as item features
 >  > * `IMDbTitleBasics.csv`, and `IMDbTitleRatings.csv`
 >  > * The 1100 **genome tags** from MovieLens also as item features
 >  > * `genome-tags.csv`

### User-Item Tx Matrix

#### `ratings.csv`

 > 
 >  > 
 >  > This is the user-item transaction matrix. The only `userId`'s are `1` in this screenshot simply because it is ordered in ascending order (so this is viewing all of user `1`'s interactions but it ascends to user `2` and so on).

<div style="max-width: 100%; overflow: hidden;">
  <img src="doc/fig/Screenshot%202023-07-01%20at%2019.38.54.png" style="max-width: 100%; height: auto;">
</div>


### Features

 > 
 >  > 
 >  > These are the features used for content-based techniques.

In the *deep hybrid* experiments, features are extracted (engineered) from the [IMDbTitleBasics.csv](https://www.kaggle.com/datasets/komalkhetlani/imdb-dataset) and the [IMDbTitleRatings.csv](https://www.kaggle.com/datasets/komalkhetlani/imdb-dataset). A pre-processing script extracts and computes a feature dataframe from the following subfeatures present in either csv:

* **Genres**: *Multi-hot encoded representation of genres*
* **Personnel**: \*Multi-hot encoded representation of personnel involved in the movie (actors, directors, etc.)
* **Genome Tags**: *Multi-hot encoded representation of genome tags associated with the movie*
  The code that performs the feature extraction over these two datasets to construct a single feature dataset for export can be found [here](https://github.com/michaelbzms/DeepRecommendation/blob/main/src/create_dataset.ipynb).

For our application, we can simplify this by providing a single *metadata.csv* dataset that would contain song metadata. This could contain the following columns: \[song_id, artist_id, release, year, genre, bpm, tags\]. From there, we can multi-hot encode the genres, and genome tags (though we may want to one-hot encode the artist_id instead of multi-hot-encoding it? will check back on this later when needed).

### Custom (User-defined) Features

#### `genome-tags.csv`

 > 
 >  > 
 >  > These are basically *extra features* in the form of *custom tags* (can be thought of like *hashtags*)


<div style="max-width: 100%; overflow: hidden;">
  <img src="doc/fig/Screenshot%202023-07-01%20at%2019.53.10.png" style="max-width: 100%; height: auto;">
</div>

# Integration

The path to integration is *pretty* simple, but there's some things we should take into consideration:

#### User-Item Tx Pairings

1. Designing the ***user-item tx matrix***:
   * We need to define our schema for the user-item rating pairs.
   
   * I don't think listen_counts are a good rating metric. Because they are high variance, they are just one more thing to have to normalize in pre-processing. 
     
     ````Python
     class UserItemRatings:
     	user_id: string,
     	song_id: string,
     	# Use 0.0 to 5.0 rating instead of listen_counts
     	rating: float,
     
     # As pd.DataFrame
     # 
     # | user_id | song_id | rating |
     # | ------- | ------- | ------ |
     # |  42424  | 1931093 |   5.0  |
     ````

#### Persisting the User-Item Tx Pairings

2. We also need to decide how we want to *persist* the user-item ratings:
   * Could be stored in a lightweight K/V such as ***rocks*** and updated dynamically,
     * could have `key((user_id, song_id)) -> float`
   * ***or***, add it as a record into an existing PostgreSQL and slot it's CRUD into an existing service

#### Handling Interactions Dynamically

3. Design ***the algorithm for dynamically updating ratings*** weighted against some new *interaction*.
   
   * This will allow us to keep a score of a user's rating of an item *dynamically* as they interact with it. This can be done by assigning weights to interactions (like, download, buy) and fixing the range of output from 0.0 to 5.0.
     
     ````Python
     	# Can be adjusted on 0 to 1
     	weights = {"buy": 1.0, "download": 0.8, "like": 0.6, "listen": 0.2}
     
     	# Run this when a user interacts with an item.
     	#
     	# For instance, the beat handler could integrate this middleware
     	# on 'like' events. Or, we could create a new gRPC microservice that
     	# can be dispatched to handle this logic.
     	def handle_interaction_dynamics(
     		user_id: str, 
     		song_id: str, 
     		# The weight should be in range 0 to 1
     		interaction_weight: float
     		):
     		max_positive = 1.0
     		delta = max_positive * interaction_weight
     		new_rating = curr_rating + delta
     		# can't exceed 5.0
     		new_rating = max(0.0, min(new_rating, 5.0)) 
     		
     		return new_rating
     ````

3. *Integrate* the `handle_interaction_dynamics` logic as middleware for handlers that operate on interactions.
   
   * This will allow us to start collecting and dynamically updating user-item ratings.

#### Serving the Data

5. Decide how we want to ***serve the user-item pairings and song metadata*** datasets to our *training code*. Be that as a *new microservice*, **or** *new methods extending existing services*.

#### Make Necessary Modifications to [DeepRecommendation](https://github.com/michaelbzms/DeepRecommendation)

6. Lastly, we must make the necessary tweaks to the source code to complete integration.
   * Generously, the README tells us exactly what we need to modify to adapt this code for our application.
     * We will need to *implement our own content providers by extending the abstract classes, as shown [here](https://github.com/michaelbzms/DeepRecommendation/blob/main/src/content_providers/one_hot_provider.py). We'll need to do this for both the `OneHotProvider` (handles user-item pairing preprocessing) as well as the `DynamicProfilesProvider` (handles feature preprocessing from song metadata). We may also need to change some hardcoded logic in the [datasets]()* *directory*. *Everything else should be good to go*
     * This probably includes changing the path to various `.csv` files we want to load, like our `ratings.csv` and `metadata.csv` files. Most paths seem to be globally defined in `global.py`
   * We will also need to write a small pre-processing script that runs before any calls to ***deep hybrid***. This is because we need to multi-hot / one-hot encode the features from `metadata.csv` and output it to a valid file that ***deep hybrid*** will read from it's *data* directory.
