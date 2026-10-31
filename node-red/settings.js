/**
 * Node-RED runtime settings for the Smart Fishing project.
 * The Docker Compose service mounts this directory at /data, Node-RED's userDir.
 */
module.exports = {
    flowFile: 'flows/smart-fishing.json',
    credentialSecret: process.env.NODE_RED_CREDENTIAL_SECRET,
    uiPort: 1880
};
