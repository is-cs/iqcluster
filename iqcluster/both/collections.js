import { Mongo } from 'meteor/mongo';

// export const ClusterStats = new Mongo.Collection('ClusterStats');
export const mcJobs = new Mongo.Collection("Jobs");
export const nodeStats = new Mongo.Collection("nodestats");

