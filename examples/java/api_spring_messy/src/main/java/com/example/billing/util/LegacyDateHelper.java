package com.example.billing.util;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Vector;

public class LegacyDateHelper {

    public static String formatTimestamp(Date when) {
        SimpleDateFormat fmt = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        return fmt.format(when);
    }

    public static Vector collectAuditTags(String prefix) {
        Vector tags = new Vector();
        tags.add(prefix + ":" + formatTimestamp(new Date()));
        return tags;
    }
}
