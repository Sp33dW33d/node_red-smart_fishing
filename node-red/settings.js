/**
 * Node-RED runtime settings for the Smart Fishing project.
 * The Docker Compose service mounts this directory at /data, Node-RED's userDir.
 */
if (process.env.NODE_RED_FORCE_IPV4 === 'true') {
    // Some Docker-in-WSL hosts resolve IPv6 but cannot route it; prefer IPv4 for HTTPS.
    require('https').globalAgent.options.family = 4;
}

module.exports = {
    flowFile: 'flows/smart-fishing.json',
    credentialSecret: process.env.NODE_RED_CREDENTIAL_SECRET,
    uiPort: 1880
};
