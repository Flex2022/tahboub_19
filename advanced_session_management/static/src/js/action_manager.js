/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { rpc } from "@web/core/network/rpc";

async function getClientIp(ipParams) {
    if (!ipParams.ip_key || !ipParams.ip_url) {
        return null;
    }
    try {
        const response = await fetch(ipParams.ip_url, { method: "GET" });
        if (!response.ok) {
            return null;
        }
        const ipJson = await response.json();
        return ipJson[ipParams.ip_key] || null;
    } catch {
        return null;
    }
}

async function postActionData(url) {
    try {
        const ipParams = await rpc("/get/ip_params", {});
        if (!ipParams || !ipParams.ip_key || !ipParams.ip_url) {
            return;
        }
        const clientIp = await getClientIp(ipParams);
        await rpc("/post/action_data", {
            data: url,
            ip: clientIp,
        });
    } catch {
        // Ignore telemetry failures so hash changes never break the UI.
    }
}

browser.addEventListener("hashchange", () => {
    postActionData(browser.location.href);
});
