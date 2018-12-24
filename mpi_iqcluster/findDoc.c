#include <bson.h>
#include <mongoc.h>
#include <stdio.h>

int main (int argc, char *argv[])
{
   mongoc_client_t *client;
   mongoc_collection_t *collection;
   mongoc_cursor_t *cursor;
   const bson_t *doc;
   bson_t *query;
   char *str;
   bson_iter_t iter;
   bson_iter_t cmd_iter;
   const char* cmd;
   uint32_t cmd_len;
   bson_iter_t userId_iter;
   const char* userId;
   uint32_t userId_len;
   bson_iter_t queue_iter;
   const char* queue;
   uint32_t queue_len;
   bson_iter_t state_iter;
   const char* state;
   uint32_t state_len;
   bson_iter_t exclude_iter;
   uint32_t ex_len;
   const uint8_t* ex_arr;
   bson_t *ex_doc;
   bson_iter_t ex_doc_iter;
   const char* idx[4] = {"0","1","2","3"};

   mongoc_init ();

   client =
      mongoc_client_new ("mongodb://isingh:FreePass123@ds155293.mlab.com:55293/iqcluster");
   collection = mongoc_client_get_collection (client, "iqcluster", "Jobs");
   query = bson_new ();
   cursor = mongoc_collection_find_with_opts (collection, query, NULL, NULL);

   while (mongoc_cursor_next (cursor, &doc)) {
      str = bson_as_canonical_extended_json (doc, NULL);
      printf ("%s\n", str);
      bson_iter_init(&iter, doc);
      bson_iter_find_descendant(&iter, "cmd", &cmd_iter);
      cmd=bson_iter_utf8(&cmd_iter,&cmd_len);
      printf("cmd=%s\n",cmd);
      bson_iter_init(&iter, doc);
      bson_iter_find_descendant(&iter, "userId", &userId_iter);
      userId=bson_iter_utf8(&userId_iter,&userId_len);
      if(userId)
        printf("userId=%s\n",userId);
      else
        printf("userId null\n");
      bson_iter_init(&iter, doc);
      bson_iter_find_descendant(&iter, "queue", &queue_iter);
      queue=bson_iter_utf8(&queue_iter,&queue_len);
      printf("queue=%s\n",queue);
      bson_iter_init(&iter, doc);
      bson_iter_find_descendant(&iter, "state", &state_iter);
      state=bson_iter_utf8(&state_iter,&state_len);
      printf("state=%s\n",state);
      bson_iter_init(&iter, doc);
      bson_iter_find_descendant(&iter, "exclude", &exclude_iter);
      bson_iter_array(&exclude_iter, &ex_len, &ex_arr);
      ex_doc = bson_new_from_data(ex_arr, ex_len);
      ex_len=bson_count_keys(ex_doc);
      printf("num excludes: %d\n", ex_len);
      bson_destroy(ex_doc); 
      bson_free (str);
   }

   bson_destroy (query);
   mongoc_cursor_destroy (cursor);
   mongoc_collection_destroy (collection);
   mongoc_client_destroy (client);
   mongoc_cleanup ();

   return 0;
}
