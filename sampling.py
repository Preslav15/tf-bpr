import random
import numpy

class Sampling(object):
  def generate_train_batch():
    raise "Implement in subclass"
  
  def generate_user_eval_batch():
    raise "Implement in subclass"
    
class PeymanSampling(Sampling):
  def generate_train_batch():
    raise "Not implemented yet..."
  
  def generate_user_eval_batch():
    raise "Not implemented yet..."
  
class Uniform(Sampling):
  def generate_train_batch(self, user_items, val_ratings, test_ratings, item_count, image_features, sample_count=400, batch_size=512):
    for i in xrange(sample_count):
        t = []
        iv = []
        jv = []
        for b in xrange(batch_size):
            u = random.randint(1, len(user_items))
            
            i = random.sample(user_items[u], 1)[0]
            while i == test_ratings[u] or i==val_ratings[u]: #make sure i is not in the test or val set
                i = random.sample(user_items[u], 1)[0]
            
            j = random.randint(0, item_count)
            while j in user_items[u]: #make sure j is not in users reviews (ie it is negative)
                j = random.randint(0, item_count)
            
            #sometimes there will not be an image for given item i or j
            if image_features:
              try:
                image_features[i]
                image_features[j]
              except KeyError:
                continue  #if so, skip this item
            
            t.append([u, i, j])
            
            if image_features:
              iv.append(image_features[i])
              jv.append(image_features[j])
        
        if image_features:      
          yield numpy.asarray(t), numpy.vstack(tuple(iv)), numpy.vstack(tuple(jv))
        else:
          yield numpy.asarray(t)
        
  def generate_user_eval_batch(self, user_items, test_ratings, item_count, item_dist, image_features, sample_size=3000, neg_sample_size=1000, cold_start=False):
      # using leave one cv
      for u in random.sample(test_ratings.keys(), sample_size): #uniform random sampling w/o replacement
          t = []
          ilist = []
          jlist = []
        
          i = test_ratings[u]
          #check if we have an image for i, sometimes we dont...
          if image_features and i not in image_features:
            continue
        
          #filter for cold start
          if cold_start and item_dist[i] > 5:
            continue
        
          for _ in xrange(neg_sample_size):
              j = random.randint(1, item_count)
              if j != test_ratings[u] and not (j in user_items[u]):
                  # find negative item not in train or test set
                
                  #sometimes there will not be an image for given product
                  if image_features:
                    try:
                      image_features[i]
                      image_features[j]
                    except KeyError:
                      continue  #if image not found, skip item
                
                  t.append([u, i, j])
                  
                  if image_features:
                    ilist.append(image_features[i])
                    jlist.append(image_features[j])
        
          if image_features:
            yield numpy.asarray(t), numpy.vstack(tuple(ilist)), numpy.vstack(tuple(jlist))
          else:
            yield numpy.asarray(t)
    
  
if __name__ == '__main__':
  import corpus

  users, items, reviews, user_dist, item_dist, user_items, item_users = corpus.Corpus.load_reviews("data/amzn/reviews_Women_ALL_scraped.csv")
  item_count = len(item_users)
  image_features = corpus.Corpus.load_images("data/amzn/image_features_Women.b", items)
  val_ratings, test_ratings = corpus.Corpus.generate_val_and_test(user_items)
  sampler = Uniform()
  for batch in sampler.generate_train_batch(user_items, val_ratings, test_ratings, item_count, image_features, sample_count=10, batch_size=10):
    uij=batch[0]
    print uij